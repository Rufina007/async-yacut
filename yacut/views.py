from http import HTTPStatus

from flask import abort, flash, redirect, render_template

from . import app
from .disk import async_upload_files_to_disk
from .exceptions import ShortIDExistsError, ShortIDGenerationError
from .forms import FilesForm, ShortenerForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = ShortenerForm()
    if form.validate_on_submit():
        try:
            url_map = URLMap.create(
                form.original_link.data, form.custom_id.data
            )
        except (ShortIDExistsError, ShortIDGenerationError) as error:
            flash(str(error))
            return render_template('index.html', form=form)
        return render_template(
            'index.html', form=form, short_link=url_map.get_short_link()
        )
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if form.validate_on_submit():
        uploaded_files = await async_upload_files_to_disk(form.files.data)
        files_links = []
        for filename, download_url in uploaded_files:
            url_map = URLMap.create(download_url)
            files_links.append((filename, url_map.get_short_link()))
        return render_template(
            'files.html', form=form, files_links=files_links
        )
    return render_template('files.html', form=form)


@app.route('/<short_id>')
def redirect_view(short_id):
    url_map = URLMap.get_by_short_id(short_id)
    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)
