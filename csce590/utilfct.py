
import mne
import requests
import warnings

import numpy as np


def download_file_from_google_drive(id, destination):
    def get_confirm_token(response):
        for key, value in response.cookies.items():
            if key.startswith('download_warning'):
                return value

        return None

    def save_response_content(response, destination):
        chunk_size = 32768

        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

    url = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(url, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(url, params=params, stream=True)

    save_response_content(response, destination)

def plot_values_topomap(value_dict, montage, axes, colorbar=True, cmap='RdBu_r',
                        vmin=None, vmax=None, names=None, image_interp='cubic', side_cb="right",
                        sensors=True, **kwargs):
    if names is None:
        names = [ch_name for ch_name in montage.ch_names if ch_name in value_dict]

    info = mne.create_info(names, sfreq=256, ch_types="eeg")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mne.io.RawArray(np.zeros((len(names), 1)), info, copy=None, verbose=False).set_montage(montage)

    im = mne.viz.plot_topomap([value_dict[ch] for ch in names], pos=info, show=False, image_interp=image_interp,
                      sensors=sensors, res=64, axes=axes, names=names,
                      vlim=(vmin, vmax), cmap=cmap, **kwargs)

    if colorbar:
        try:
            cbar, cax = mne.viz.topomap._add_colorbar(axes, im[0], cmap, pad=.05,
                                      format='%3.2f', side=side_cb)
            axes.cbar = cbar
            cbar.ax.tick_params(labelsize=12)

        except TypeError:
            pass

    return im

