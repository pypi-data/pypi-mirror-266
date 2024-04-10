Cascadis
=========

A content-addressed storage service.

This project is currently at experimental stage.

Install with `pip`:

    pip install cascadis

For deployment, you may want to use `gunicorn`:

    pip install gunicorn
    gunicorn -w 8 cascadis.api:app -b 0.0.0.0:16000 
