import shutil, os


def clear_contents(saving_dir, log=None):
    if os.path.exists(saving_dir):
        if log: log.log(f'CLEARING RESULT DATA ON {saving_dir}.')
        shutil.rmtree(saving_dir)
    os.mkdir(f'{saving_dir}/')
