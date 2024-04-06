# DRF Blog Bridger

## Introduction

DRF Blog Bridger is a simple tool that allows Django Rest Framework Developers to set up a simple blog API without worrying about the underlying code. The tool takes care of things like CRUD operations for blog posts, as well as the comment feature for each post.

## Getting Started

The following instructions will help you install DRF Blog Bridger on your local system and have it running. You can read the [full documentation on Read The Docs](https://drf-blog-bridger.readthedocs.io/en/latest/).

### Prerequisites

- Python 3.8 or higher
- Pip
- Django Rest Framework

### Installation and Setup
1. Install the package with:

    ```bash
    pip install drf_blog_bridger
    ```

2. Include the following settings in your `settings.py` file:
    ```python
    INSTALLED_APPS = [

        'blog_bridger_drf',
        'rest_framework',
    ]

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES':[
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ]
    }
    ```
3. Include the following in your project-level `urls.py` file:
    ```python
    path('api/posts/', include('blog_bridger_drf.urls')),
    ```
4. Run `python manage.py migrate` to migrate the models into your database. You should read the [API reference](https://drf-blog-bridger.readthedocs.io/en/latest/api_docs/) to understand how the endpoints work.
