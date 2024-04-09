import glob
import os.path
import random

from gxl_ai_utils.utils import utils_file

def data_handle():
    """"""
    input_raw_dir = "/home/node36_data/xlgeng/asr_data_from_pachong/gxl_output/lizhi_jiankang"
    text_with_puncuation = os.path.join(input_raw_dir, "text_with_punctuation")
    wav_path = os.path.join(input_raw_dir, "wav.scp")
    output_dir = "/home/work_nfs14/xlgeng/asr_data_shard/pachong_data/4_lizhi_jiankang_punctuation"
    os.makedirs(output_dir, exist_ok=True)
    utils_file.do_make_shard_file(wav_path, text_with_puncuation, output_dir)
    utils_file.copy_file(os.path.join(output_dir, "shards_list.txt"),"/home/work_nfs8/xlgeng/new_workspace/wenet_gxl_salmonn/examples/aishell/salmonn/data_list/litle_data_with_puncuation_list.list")


def do_get_random_sublist(input_list, num):
    """"""
    return [input_list[i] for i in sorted(random.sample(range(len(input_list)), num))]
def data_prepare_2():
    """"""
    aishell_dir = "/home/local_data/hwang/huawei_cn_en/cn/aishell1/"
    aishell_list = glob.glob(os.path.join(aishell_dir, "*.tar"))
    punctuation_path = utils_file.load_list_file_clean("/home/work_nfs8/xlgeng/new_workspace/wenet_gxl_salmonn/examples/aishell/salmonn/data_list/litle_data_with_puncuation_list.list")
    aishell_list_little = do_get_random_sublist(aishell_list, 100)
    punctuation_list_little = do_get_random_sublist(punctuation_path, 100)
    output_path = "/home/work_nfs8/xlgeng/new_workspace/wenet_gxl_salmonn/examples/aishell/salmonn/data_list/mix_tast.list"
    res_list = []
    for aishell_list_little_i in aishell_list_little:
        temp_i = f'{aishell_list_little_i}\t0'
        res_list.append(temp_i)
    for punctuation_list_little_i in punctuation_list_little:
        temp_i = f'{punctuation_list_little_i}\t1'
        res_list.append(temp_i)
    random.shuffle(res_list)
    utils_file.write_list_to_file(res_list, output_path)



if  __name__ == "__main__":
    data_prepare_2()