# Master Blog API

This is a simple Flask backend for a blog API.

## Features

- Create, retrieve, update, delete, and search for blog posts.
- Rate limiting to prevent abuse.
- CORS enabled for all routes.

## Installation

1. Clone the repository.
2. Navigate to the `backend` directory.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command in the `backend` directory:

```bash
python backend_app.py
```

The application will be available at `http://localhost:5002`.

## API Endpoints

- `GET /api/posts`: Get all posts.
  - Query parameters:
    - `sort`: Sort by 'title' or 'content'.
    - `direction`: Sort direction 'asc' or 'desc'.
- `POST /api/posts`: Create a new post.
  - Request body:
    ```json
    {
      "title": "New Post Title",
      "content": "New post content."
    }
    ```
- `DELETE /api/posts/<post_id>`: Delete a post by ID.
- `PUT /api/posts/<post_id>`: Update a post by ID.
  - Request body:
    ```json
    {
      "title": "Updated Post Title",
      "content": "Updated post content."
    }
    ```
- `GET /api/posts/search`: Search for posts.
  - Query parameters:
    - `title`: Search by title.
    - `content`: Search by content.
