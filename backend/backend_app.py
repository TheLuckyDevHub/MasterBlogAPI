"""
A simple Flask backend for a blog API.

This module implements a basic RESTful API for managing blog posts.
It supports creating, retrieving, updating, deleting, and searching for posts.
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import os
from flask_swagger_ui import get_swaggerui_blueprint

__IS_DEBUG = True


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file


swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Configure logging
if __IS_DEBUG:
    LOGGING_PATH = os.path.join(os.path.dirname(__file__), 'logging/app.log')
    if not os.path.exists(os.path.dirname(LOGGING_PATH)):
        os.makedirs(os.path.dirname(LOGGING_PATH))
    logging.basicConfig(
        filename=LOGGING_PATH,
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )


limiter = Limiter(app=app, key_func=get_remote_address)

POSTS = [
    {"id": 1,
     "title": "First post", 
     "content": "This is the first post."
    },

    {"id": 2,
     "title": "Second post",
     "content": "This is the second post."
     },
]


def get_next_id(posts: list[dict[str, str]]) -> int:
    """
    Calculates the next available ID for a new blog post.
    """
    if not posts:
        return 1
    try:
        # Find the highest existing ID and add 1
        return max(post["id"] for post in posts) + 1
    except (KeyError, TypeError) as e:
        raise KeyError("Could not determine next ID due to invalid post data.") from e


def get_blog_post_by_id(post_id: int) -> dict[str, str] | None:
    """
    Retrieves a single blog post by its ID.
    Returns the post dictionary or None if not found.
    """
    for post in POSTS:
        if post.get("id") == post_id:
            return post
    return None


def add_blog_post(title: str, content: str) -> dict:
    """
    Adds a new blog post to the list of posts.

    Args:
        title: The title of the new post.
        content: The content of the new post.

    Returns:
        The newly created post dictionary.
    """
    id = get_next_id(POSTS)
    post = {'id': id, 'title': title, 'content': content}
    print(post)
    POSTS.append(post)
    return post


def find_str(search_str, search_key):
    """
    Searches for a string in a specific key of the post dictionaries.

    Args:
        search_str: The string to search for.
        search_key: The key in the dictionary to search ('title' or 'content').

    Returns:
        A list of posts that match the search criteria.
    """
    if not search_str or not search_key:
        return []
    return [post for post in POSTS if search_str.lower() in post[search_key].lower()]


def find_in_title(title: str):
    """
    Finds posts by searching for a string in their titles.

    Args:
        title: The string to search for in the post titles.

    Returns:
        A list of posts that have the string in their title.
    """
    return find_str(title, 'title')


def find_in_content(content: str):
    """
    Finds posts by searching for a string in their content.

    Args:
        content: The string to search for in the post content.

    Returns:
        A list of posts that have the string in their content.
    """
    return find_str(content, 'content')


def sort_posts_by_(key: str, is_desc: bool) -> list[dict]:
    """
    Sorts the list of posts by a given key and direction.

    Args:
        key: The key to sort by ('title' or 'content').
        is_desc: The direction to sort in (True for descending, False for ascending).

    Returns:
        A new list of posts sorted as specified.
    """
    return sorted(POSTS, key=lambda d: d[key], reverse=is_desc)


@app.route('/api/posts', methods=['GET'])
@limiter.limit("100/minute")  # Limit to 100 requests per minute
def get_posts():
    """
    Handles GET requests to /api/posts.

    Returns a list of all posts, or a sorted list if sorting parameters are provided.
    'sort' and 'direction' are expected as query parameters.

    Returns:
        A JSON response with the list of posts and a status code.
    """
    sort = request.args.get('sort')
    dir = request.args.get('direction')
    if sort and dir:
        if (sort == 'title' or sort == 'content') and (dir == "asc" or dir == "desc"):
            sorted_list = sort_posts_by_(sort, dir == "desc")
            return jsonify(sorted_list), 200
        else:
            return {
                     'message': 'Wrong sort or direction value'
                }, 400

    return jsonify(POSTS), 200


@app.route('/api/posts', methods=['POST'])
@limiter.limit("100/minute")  # Limit to 100 requests per minute
def add_post():
    """
    Handles POST requests to /api/posts.

    Creates a new post from the JSON data in the request.
    'title' and 'content' are expected in the JSON body.

    Returns:
        A JSON response with the new post and a 201 status code, or an error message.
    """
    post_json = request.get_json()

    if request.method == "POST":
        post = add_blog_post(
            post_json['title'],
            post_json['content']
        )

        return jsonify(post), 201

    return 'Post can not added', 404


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@limiter.limit("100/minute")  # Limit to 100 requests per minute
def delete_post(post_id):
    """
    Handles DELETE requests to /api/posts/<post_id>.

    Deletes a post by its ID.

    Args:
        post_id: The ID of the post to delete.

    Returns:
        A JSON response with a success message or a 404 error if the post is not found.
    """
    post = get_blog_post_by_id(post_id)
    if post:
        POSTS.remove(post)
        return {
            'message': f"Post with id {post_id} has been deleted successfully."
        }, 200

    return {
        'message': f'Post with id= {post_id} not found'
        }, 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@limiter.limit("100/minute")  # Limit to 100 requests per minute
def update_post(post_id):
    """
    Handles PUT requests to /api/posts/<post_id>.

    Updates a post with the JSON data in the request.
    'title' and 'content' are expected in the JSON body.

    Args:
        post_id: The ID of the post to update.

    Returns:
        A JSON response with the updated post or a 404 error if the post is not found.
    """
    post = get_blog_post_by_id(post_id)
    if post:
        post_json = request.get_json()
        post['title'] = post_json['title']
        post['content'] = post_json['content']

        return jsonify(post), 200

    return {
        'message': f'Post with id= {post_id} not found'
        }, 404


@app.route('/api/posts/search', methods=['GET'])
@limiter.limit("100/minute")  # Limit to 100 requests per minute
def get_posts_search():
    """
    Handles GET requests to /api/posts/search.

    Searches for posts by title or content.
    'title' or 'content' are expected as query parameters.

    Returns:
        A JSON response with the search results or a 404 error if no search term is provided.
    """

    title = request.args.get('title')
    if title:
        return jsonify(find_in_title(title)), 200

    content = request.args.get('content')
    if content:
        return jsonify(find_in_content(content)), 200

    return [], 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=__IS_DEBUG)
