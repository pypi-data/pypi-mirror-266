import os


def main():
    rank = os.environ.get('RANK')
    haplo_session_directory = os.environ.get('HAPLO_SESSION_DIRECTORY')
    print(f'{rank}: {haplo_session_directory}')


if __name__ == '__main__':
    main()
