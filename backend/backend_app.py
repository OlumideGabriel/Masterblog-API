from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
            {"id": 1,
             "title": "First post",
             "content": "This is the first post.",
             'author': 'Gabriel',
             'date': 'June 11, 2024'},

            {"id": 2,
             "title": "Second post",
             "content": "This is the second post.",
             'author': 'Gabriel',
             'date': "June 11, 2024"}
        ]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort', None)
    sort_direction = request.args.get('direction', 'asc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    # Check for valid sort fields and directions
    if sort_field and sort_field not in ['title', 'content', 'author', 'date']:
        return jsonify({"error": "Invalid sort field. Must be 'title', 'content', 'author', or 'date'."}), 400

    if sort_direction not in ['asc', 'desc']:
        return jsonify({"error": "Invalid sort direction. Must be 'asc' or 'desc'."}), 400

    sorted_posts = POSTS[:]
    if sort_field:
        reverse = sort_direction == 'desc'
        if sort_field == 'date':
            sorted_posts = sorted(sorted_posts, key=lambda x: datetime.strptime(x['date'], "%B %d, %Y"), reverse=reverse)
        else:
            sorted_posts = sorted(sorted_posts, key=lambda x: x[sort_field].lower(), reverse=reverse)

    start = (page - 1) * limit
    end = start + limit
    paginated_posts = sorted_posts[start:end]

    return jsonify(paginated_posts)


@app.route('/api/posts', methods=['POST'])
def add_post():
    new_post = request.get_json()
    if not new_post or 'title' not in new_post or 'content' not in new_post:
        return jsonify({"error": "Invalid request, title and content are required."}), 400
    new_post['id'] = len(POSTS) + 1
    new_post['author'] = new_post.get('author', 'default_author')  # Set default author
    new_post['date'] = datetime.now().strftime("%B %d, %Y")
    POSTS.append(new_post)
    return jsonify({"message": "Post added successfully.", "post": new_post}), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    for post in POSTS:
        if post['id'] == id:
            POSTS.remove(post)
            return jsonify({"message": f"Post with {id} deleted successfully."}), 200

    return jsonify({"error": "Post does not exist."}), 404


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    update_data = request.get_json()
    if not update_data or 'title' not in update_data or 'content' not in update_data:
        return jsonify({"error": "Invalid request, title and content are required."}), 400

    for post in POSTS:
        if post['id'] == id:
            post['title'] = update_data['title']
            post['content'] = update_data['content']
            post['author'] = update_data['author']
            post['date_modified'] = datetime.now().strftime("%B %d, %Y")
            return jsonify({"message": f"Post with id {id} updated successfully.", "post": post}), 200

    return jsonify({"error": "Post does not exist."}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()
    author_query = request.args.get('author', '').lower()
    date_query = request.args.get('date', '')

    # Filter posts by title, content, author, and date
    matching_posts = [
        post for post in POSTS
        if (title_query in post['title'].lower() if title_query else True)
        and (content_query in post['content'].lower() if content_query else True)
        and (author_query in post['author'].lower() if author_query else True)
        and (date_query == post['date'] if date_query else True)
    ]

    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
