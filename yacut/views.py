import string
from random import choice

from flask import redirect, render_template, url_for

from . import app, db
from .disk import async_upload_files_to_disk
from .forms import FilesForm, ShortenerForm
from .models import URLMap

SHORT_ID_LENGTH = 6
SHORT_ID_ALPHABET = string.ascii_letters + string.digits


def generate_short_id():
    return ''.join(choice(SHORT_ID_ALPHABET) for _ in range(SHORT_ID_LENGTH))


def get_unique_short_id():
    short_id = generate_short_id()
    while URLMap.query.filter_by(short=short_id).first() is not None:
        short_id = generate_short_id()
    return short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = ShortenerForm()
    if form.validate_on_submit():
        short = form.custom_id.data or get_unique_short_id()
        url_map = URLMap(original=form.original_link.data, short=short)
        db.session.add(url_map)
        db.session.commit()
        short_link = url_for('redirect_view', short_id=short, _external=True)
        return render_template('index.html', form=form, short_link=short_link)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if form.validate_on_submit():
        uploaded_files = await async_upload_files_to_disk(form.files.data)
        files_links = []
        for filename, download_url in uploaded_files:
            short = get_unique_short_id()
            url_map = URLMap(original=download_url, short=short)
            db.session.add(url_map)
            db.session.commit()
            files_links.append((
                filename,
                url_for('redirect_view', short_id=short, _external=True)
            ))
        return render_template(
            'files.html', form=form, files_links=files_links
        )
    return render_template('files.html', form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    return redirect(url_map.original)
