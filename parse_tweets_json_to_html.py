import datetime
import json
import os
import requests
import re

class ParseTweetsJSONtoHTML():
    def __init__(self):
        self._output_html_directory = None
        self._tweets_as_json = None

        with open("config.json") as json_data_file:
            config_data = json.load(json_data_file)
            self.output_json_file_path = config_data.get('OUTPUT_JSON_FILE_PATH')
            self.download_images = config_data.get('DOWNLOAD_IMAGES')

    def write_tweets_to_html(self):
        with open(self.output_index_path, 'w') as output_html:
            output_html.write('<html><head>')
            output_html.write('<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1.0, maximum-scale=1.0" />')
            output_html.write('<title>Liked Tweets Export</title>')
            output_html.write('<link rel="stylesheet" href="styles.css"></head>')
            output_html.write('<body><h1>Liked Tweets</h1><div class="tweet_list">')
            for tweet_data in self.tweets_as_json:
                tweet_html = self.create_tweet_html(tweet_data)
                output_html.write(tweet_html)
            output_html.write('</div></body></html>')

    def create_tweet_html(self, tweet_data):
        output_html = '<div class="tweet_wrapper">'

        if self.download_images:
            user_image_src = f'images/avatars/{tweet_data["user_id"]}.jpg'
            full_path = f"{self.output_html_directory}/{user_image_src}"
            self.save_remote_image(tweet_data["user_avatar_url"], full_path)
        else:
            user_image_src = tweet_data["user_avatar_url"]
        
        output_html += '<div class="tweet_author_wrapper">'
        output_html += f"<div class='tweet_author_image'><img loading='lazy' src='{user_image_src}'></div>"
        output_html += "<div class='author_context'><div class='tweet_author_handle'>"
        output_html += f"<a href='https://www.twitter.com/{tweet_data['user_handle']}/' target='_blank'>"
        output_html += f"@{self.parse_text_for_html(tweet_data['user_handle'])}</a></div>"
        output_html += f"<div class='tweet_author_name'>{self.parse_text_for_html(tweet_data['user_name'])}</div>"
        output_html += '</div></div>\n'

        output_html += f"<div class='tweet_content'>{self.parse_text_for_html(re.sub('https://t.co/.*', '', tweet_data['tweet_content']))}</div>"

        if tweet_data["tweet_media_urls"]:
            output_html += "<div class='tweet_images_wrapper'>"
            for media_url in tweet_data["tweet_media_urls"]:
                if self.download_images:
                    media_name = media_url.split("/")[-1]
                    user_image_path = f'images/tweets/{media_name}'
                    full_path = f"{self.output_html_directory}/{user_image_path}"
                    self.save_remote_image(media_url, full_path)
                else:
                    user_image_path = media_url
                output_html += f"<div class='tweet_image'><a href='{user_image_path}' target='_blank'><img loading='lazy' src='{user_image_path}'></a></div>"
            output_html += "</div>\n"

        if tweet_data['quote']:
            output_html += self.create_tweet_html(tweet_data['quote'])

        output_html += "<div class='tweet_reactions'><div class='st-div'>"
        output_html += "<svg class='icon' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path fill='currentColor' d='M123.6 391.3c12.9-9.4 29.6-11.8 44.6-6.4c26.5 9.6 56.2 15.1 87.8 15.1c124.7 0 208-80.5 208-160s-83.3-160-208-160S48 160.5 48 240c0 32 12.4 62.8 35.7 89.2c8.6 9.7 12.8 22.5 11.8 35.5c-1.4 18.1-5.7 34.7-11.3 49.4c17-7.9 31.1-16.7 39.4-22.7zM21.2 431.9c1.8-2.7 3.5-5.4 5.1-8.1c10-16.6 19.5-38.4 21.4-62.9C17.7 326.8 0 285.1 0 240C0 125.1 114.6 32 256 32s256 93.1 256 208s-114.6 208-256 208c-37.1 0-72.3-6.4-104.1-17.9c-11.9 8.7-31.3 20.6-54.3 30.6c-15.1 6.6-32.3 12.6-50.1 16.1c-.8 .2-1.6 .3-2.4 .5c-4.4 .8-8.7 1.5-13.2 1.9c-.2 0-.5 .1-.7 .1c-5.1 .5-10.2 .8-15.3 .8c-6.5 0-12.3-3.9-14.8-9.9c-2.5-6-1.1-12.8 3.4-17.4c4.1-4.2 7.8-8.7 11.3-13.5c1.7-2.3 3.3-4.6 4.8-6.9c.1-.2 .2-.3 .3-.5z'/></svg>"
        output_html += f"<div class='reactions_number'>{tweet_data['tweet_reply_count']}</div>"
        output_html += "</div><div class='nd-div'>"
        output_html += "<svg class='icon' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 576 512'><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path fill='currentColor' d='M272 416c17.7 0 32-14.3 32-32s-14.3-32-32-32H160c-17.7 0-32-14.3-32-32V192h32c12.9 0 24.6-7.8 29.6-19.8s2.2-25.7-6.9-34.9l-64-64c-12.5-12.5-32.8-12.5-45.3 0l-64 64c-9.2 9.2-11.9 22.9-6.9 34.9s16.6 19.8 29.6 19.8l32 0 0 128c0 53 43 96 96 96H272zM304 96c-17.7 0-32 14.3-32 32s14.3 32 32 32l112 0c17.7 0 32 14.3 32 32l0 128H416c-12.9 0-24.6 7.8-29.6 19.8s-2.2 25.7 6.9 34.9l64 64c12.5 12.5 32.8 12.5 45.3 0l64-64c9.2-9.2 11.9-22.9 6.9-34.9s-16.6-19.8-29.6-19.8l-32 0V192c0-53-43-96-96-96L304 96z'/></svg>"
        output_html += f"<div class='reactions_number'>{tweet_data['tweet_retweet_count']}</div>"
        output_html += "</div><div class='rd-div'>"
        output_html += "<svg class='icon heart-icon' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path fill='currentColor' d='M47.6 300.4L228.3 469.1c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9L464.4 300.4c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141C347 36.5 300.6 51.4 268 84L256 96 244 84c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z'/></svg>"
        output_html += f"<div class='reactions_number'>{tweet_data['tweet_like_count']}</div>"
        output_html += "</div></div>"

        parsed_datetime = datetime.datetime.strptime(tweet_data['tweet_created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        output_html += f"<div class='tweet_created_at'>{parsed_datetime.strftime('%m/%d/%Y %I:%M%p')}</div>"
        output_html += "<div class='twitter_link'>"
        output_html += f"<a href='https://www.twitter.com/{tweet_data['user_handle']}/status/{tweet_data['tweet_id']}/' target='_blank'>Original tweet &#8599;</a> &#8226; "
        individual_tweet_file_path = f"{self.output_html_directory}/tweets/{tweet_data['tweet_id']}.html"
        output_html += f"<a href='tweets/{tweet_data['tweet_id']}.html' target='_blank'>Local version</a>"
        output_html += "</div>"

        output_html += "</div>\n\n"

        
        with open(individual_tweet_file_path, 'w') as individual_tweet_file:
            individual_tweet_file.write('<html><head>')
            individual_tweet_file.write('<meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1.0, maximum-scale=1.0" />')
            individual_tweet_file.write('<title>Liked Tweets Export</title>')
            individual_tweet_file.write('<link rel="stylesheet" href="../styles.css"></head>')
            individual_tweet_file.write('<body><div class="tweet_list">')
            adjusted_html = output_html.replace("images/avatars", "../images/avatars")
            adjusted_html = adjusted_html.replace("images/tweets", "../images/tweets")
            individual_tweet_file.write(adjusted_html)
            individual_tweet_file.write('</div></body></html>')

        return output_html

    def save_remote_image(self, remote_url, local_path):
        if os.path.exists(local_path):
            return
        print(f"Downloading image {remote_url}...")
        img_data = requests.get(remote_url).content
        with open(local_path, 'wb') as handler:
            handler.write(img_data)

    def parse_text_for_html(self,input_text):
        return input_text.encode('ascii', 'xmlcharrefreplace').decode()

    @property
    def output_index_path(self):
        return f'{self.output_html_directory}/index.html'

    @property
    def output_html_directory(self):
        if not self._output_html_directory:
            script_dir = os.path.dirname(__file__)
            self._output_html_directory = os.path.join(script_dir, 'tweet_likes_html')
        return self._output_html_directory

    @property
    def tweets_as_json(self):
        if not self._tweets_as_json:
            with open(self.output_json_file_path, 'rb') as json_file:
                lines = json_file.readlines()
                self._tweets_as_json = json.loads(lines[0])

        return self._tweets_as_json

if __name__ == "__main__":
    parser = ParseTweetsJSONtoHTML()
    print(f"Saving tweets to {parser.output_index_path}...")
    parser.write_tweets_to_html()
    print(f"Done. Output file located at {parser.output_index_path}")

