from minitools import modify_file_content, delete_file_by_name

if __name__ == '__main__':
    modify_file_content('222.222.222.222', '666.666.666.666', filename='config', folder='.git')
    delete_file_by_name(filename='config', folder='.git')
    delete_file_by_name(folder='.git', deleteFolder=True)
