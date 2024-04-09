"""
Module enables running package with pck name
"""
import argparse
from .ui import App


def main():
    """
    run ai-minutes app
    """
    ttkbootstrap_themes = ['cosmo', 'flatly', 'litera', 'minty', 'lumen', 'sandstone',
                           'yeti', 'pulse', 'united', 'morph', 'journal', 'darkly',
                           'superhero', 'solar', 'cyborg', 'vapor', 'simplex', 'cerculean']
    parser = argparse.ArgumentParser(
        prog='Summarize Meetings',
        description='Create summaries from the recordings of your meetings with ChatGPT.',
        epilog='Save time by skipping listening to meeting recordings or attending meetings',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('theme', nargs='?',
                        choices=ttkbootstrap_themes, default="sandstone",
                        help="ttkbootstrap theme, (default: %(default)s)")
    args = parser.parse_args()
    app = App(args.theme)
    app.mainloop()
    app.task_queue.put(None)
    app.worker_thread.join()


if __name__ == '__main__':
    main()
