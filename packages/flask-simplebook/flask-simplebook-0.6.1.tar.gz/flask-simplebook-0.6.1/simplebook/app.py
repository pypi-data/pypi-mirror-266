import json
import subprocess
from flask import Flask, request, send_file
from rq import Queue, get_current_job
from rq.job import Job
from simplebook.worker import conn
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


app = Flask(__name__)
q = Queue(connection=conn)


def print_to_pdf(
    urls,
    page_size,
    title,
    subtitle,
    passthrough_parameters,
    username,
    password,
):
    job = get_current_job()
    params = [
        "mw2pdf",
        "pdf",
        "--title",
        title,
        "--subtitle",
        subtitle,
        "--out",
        "%s/%s.pdf" % (os.environ.get('SIMPLE_BOOK_DATA_DIR', "/tmp"),  job.id),
    ]
    if username and password:
        params.extend([
            "--mwUsername",
            username,
            "--mwPassword",
            password,
        ])
    if passthrough_parameters:
        params.extend([
            "--passthroughParameters",
            passthrough_parameters,
        ])
    if page_size:
        params.extend([
            "--pageSize",
            page_size,
        ])

    if os.environ.get('SIMPLE_BOOK_FONT'):
        params.extend([
            "--font",
            os.environ.get('SIMPLE_BOOK_FONT')
        ])

    if os.environ.get('SIMPLE_BOOK_LOGO'):
        params.extend([
            "--logo",
            os.environ.get('SIMPLE_BOOK_LOGO')
        ])

    params.extend(urls)
    subprocess.call(params)
    return


def render_book(
    book_data,
    passthrough_parameters,
    username,
    password,
):
    urls = list(map(lambda i: i["url"], book_data["items"]))
    job = q.enqueue_call(
        func=print_to_pdf,
        args=(
            urls,
            book_data.get('papersize', ''),
            book_data.get('title', ''),
            book_data.get('subtitle', ''),
            passthrough_parameters,
            username,
            password,
        ),
        result_ttl=10000,
    )
    return {"simplebook_id": job.get_id(), "is_cached": False}


def render_status():
    job = Job.fetch(request.form["simplebook_id"], connection=conn)
    status = job.get_status()
    resp = {"state": status, "response": {"status": {"progress": 0}}}
    if status == "finished":
        resp["url"] = f"http://localhost:3333/{request.form['simplebook_id']}/"
    return resp


@app.route("/", methods=["POST"])
def process_command():
    if request.form["command"] == "render":
        return render_book(
            json.loads(request.form.get('metabook', '')),
            request.form.get('passthrough_parameters', ''),
            request.form.get('login_credentials[username]', ''),
            request.form.get('login_credentials[password]', ''),
        )
    elif request.form["command"] == "render_status":
        return render_status()


@app.route("/<simplebook_id>/", methods=["POST", "GET"])
def download(simplebook_id):
    return send_file(
        f"%s/%s.pdf" % (os.environ.get('SIMPLE_BOOK_DATA_DIR', "/tmp"),  simplebook_id),
        download_name=f"{simplebook_id}.pdf"
    )
