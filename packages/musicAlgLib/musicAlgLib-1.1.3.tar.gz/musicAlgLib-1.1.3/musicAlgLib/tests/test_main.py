from  commFunction import  get_data_array, make_out_file
def Extract_Mono(audioFile):
    """
    :return:
    """
    stereo_data, frame, nchanel = get_data_array(audioFile)
    left_data = stereo_data[1::2]
    right_data = stereo_data[::2]
    l_name, r_name =audioFile[:-4] + '_L.wav', audioFile[:-4] + '_R.wav'
    make_out_file(l_name, left_data, frame, 1)
    make_out_file(r_name, right_data, frame, 1)
    return l_name, r_name


if __name__ == '__main__':
    file = '123.wav'
    Extract_Mono(file)