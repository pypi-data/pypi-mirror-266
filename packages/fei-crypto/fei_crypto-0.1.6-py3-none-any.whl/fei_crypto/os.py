import platform


def os():
    match platform.system():
        case 'Linux':
            print('linux')
            # signal.pause()
        case 'Windows':
            print('Windows')
            # os.system('pause')
        case _:
            print('other')

if __name__ == '__main__':
    os()

