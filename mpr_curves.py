# Created by Kuan Li
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import os

IOU_TH_50 = 0.5
IOU_THS = [i / 20 + 0.5 for i in range(9, -1, -1)]


class Dt:
    def __init__(self, img_id, score, bbox, mode="mPR"):
        """
        single dt
        :param img_id:
        :param score:   a list of score
        :param bbox:  bbox
        """
        self.img_id = img_id
        self.score = score
        self.bbox = bbox
        if mode == "PR50":
            self.is_match = False
        else:
            self.is_match = [False for _ in range(9, -1, -1)]  # 0.95-->0.5


class Gt:
    def __init__(self, img_id, bbox, mode="mPR"):
        """
        a gt contains a list of gt bboxes
        :param img_id:
        :param bbox:  a list of bboxes
        """
        self.img_id = img_id
        self.bbox = bbox
        if mode == "PR50":
            self.is_match = False
        else:
            self.is_match = [False for _ in range(9, -1, -1)]  # 0.95-->0.5


def compute_iou(bbox1, bbox2):
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    s_sum = w1 * h1 + w2 * h2

    left = max(x1, x2)
    right = min(x1 + w1, x2 + w2)
    top = max(y1, y2)
    bottom = min(y1 + h1, y2 + h2)

    if left >= right or top >= bottom:
        return 0
    intersect = (right - left) * (bottom - top)

    return intersect / (s_sum - intersect)


def prepare_gt_and_dt(gt_path, dt_path, c_id):
    """
    :param gt_path: gt path
    :param dt_path: dt path
    :param c_id: category_id
    :return: gt dict  and  dt list
    """
    with open(gt_path, "r") as f:
        gt = json.load(f)
        gt_objs = gt["annotations"]
        gt_imgs = gt["images"]

    gt_objs = [an for an in gt_objs if an["category_id"] == c_id]
    gt_num = len(gt_objs)
    gt_dic = dict()  # key: image_id value: a list of Gt
    for demo in gt_objs:
        if demo["image_id"] in gt_dic:
            tmp = Gt(img_id=demo["image_id"], bbox=demo["bbox"], mode=mode)
            gt_dic[demo["image_id"]].append(tmp)
        else:
            gt_dic[demo["image_id"]] = [Gt(img_id=demo["image_id"], bbox=demo["bbox"], mode=mode)]

    # TODO image_id_set should from "images", not "annotations", Done.
    # image_id_set = gt_dic.keys()  #
    image_id_set = set([im["id"] for im in gt_imgs])

    with open(dt_path, "r") as f:
        dt_objs = json.load(f)

    dt_objs = [demo for demo in dt_objs
               if demo["category_id"] == c_id and demo["image_id"] in image_id_set]

    dt_list = list()

    for demo in dt_objs:
        dt_list.append(Dt(img_id=demo["image_id"], score=demo["score"], bbox=demo["bbox"], mode=mode))

    return gt_dic, dt_list, gt_num


def match_dt_2_gt(single_dt, gts, mode="mPR"):
    """
    :param single_dt:
    :param gts: a list of gt
    :param mode:
    :return:
    """
    if mode == "PR50":
        max_iou = 0
        max_index = -1
        for index, gt in enumerate(gts):
            if not gt.is_match:
                cur_iou = compute_iou(single_dt.bbox, gt.bbox)
                if cur_iou >= IOU_TH_50 and max_iou < cur_iou:
                    max_index = index
                    max_iou = cur_iou
        if max_index >= 0:
            single_dt.is_match = True
            gts[max_index].is_match = True
    else:
        for thres_index, thres in enumerate(IOU_THS):  #first match high score
            max_iou = 0
            max_index = -1
            for index, gt in enumerate(gts):
                if not gt.is_match[thres_index]:
                    cur_iou = compute_iou(single_dt.bbox, gt.bbox)
                    if cur_iou >= thres and max_iou < cur_iou:
                        max_index = index
                        max_iou = cur_iou
            if max_index >= 0:
                single_dt.is_match[thres_index] = True
                gts[max_index].is_match[thres_index] = True


def run_match(dt_list, gt_dict, mode):
    """

    :param dt_list:  a list of Dt class
    :param gt_dict:  key: image_id  value: Gt class
    :return:
    """
    dt_list.sort(key=lambda x: x.score, reverse=True)
    # sorted(dt_list, key=lambda x: x.score)
    print("matching dt to gts...")
    for single_dt in tqdm(dt_list):
        img_id = single_dt.img_id
        # TODO img_id is exists ? Done.
        if img_id in gt_dic:
            match_dt_2_gt(single_dt, gt_dict[img_id], mode=mode)


def get_recalls_and_precisions(dt_list, gt_num, mode="mPR"):
    """
    recall: tp / gt_all;  precision:  tp/ dt_all
    :param dt_list:
    :param gt_num:
    :return:
    """
    if mode == "PR50":
        is_match = [dt.is_match for dt in dt_list]
        scores = [dt.score for dt in dt_list]
        tp_list = []
        cur_tp = 0
        for match in is_match:
            if match:
                cur_tp += 1
            tp_list.append(cur_tp)
        recalls = [(tp / gt_num) * 100 for tp in tp_list]
        precisions = [(tp / (index + 1)) * 100 for index, tp in enumerate(tp_list)]
        return recalls, precisions, scores
    else:
        recalls_all = [0 for _ in dt_list]
        precisions_all = [0 for _ in dt_list]
        scores = [dt.score for dt in dt_list]

        for index, thres in enumerate(IOU_THS):
            is_match = [dt.is_match[index] for dt in dt_list]
            tp_list = []
            cur_tp = 0
            for match in is_match:
                if match:
                    cur_tp += 1
                tp_list.append(cur_tp)
            recalls = [(tp / gt_num) * 100 for tp in tp_list]
            precisions = [(tp / (index + 1)) * 100 for index, tp in enumerate(tp_list)]
            recalls_all = [recalls_all[i]+recalls[i] for i in range(len(dt_list))]
            precisions_all = [precisions_all[i]+precisions[i] for i in range(len(dt_list))]
        recalls_all = [recall/len(IOU_THS) for recall in recalls_all]
        precisions_all = [precision/len(IOU_THS) for precision in precisions_all]
        return recalls_all, precisions_all, scores


def get_thres_index(scores, score_thres):
    indics = []
    for thres in score_thres:
        for index, score in enumerate(scores):
            if score < thres:
                indics.append(index)
                break

    return indics


if __name__ == '__main__':

    gt_coco = sys.argv[1]
    result1_json = sys.argv[2]
    result2_json = sys.argv[3]
    benchmark = sys.argv[4]
    gt_path = gt_coco
    dt_paths = [result1_json, result2_json]
    colors = ['red', 'green', 'blue', "cyan", "brown", "black", "orange"]  # default color
    labels = ['v6.1_nnie', 'v6.2_nnie']  # same length as dt_paths
    c_id = 1  # filter category_id
    c_labels = {1: "body", 2: "head", 3: "face"}
    mode = "mPR"  # mPR or PR50
    #score_thres = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]  # suggestion: descend, plot some key points
    #score_marker = ["o", "v", "+", "s", ">", "*", "<"]  # marker
    score_thres = [0.8, 0.7, 0.6, 0.5]  # suggestion: descend, plot some key points
    score_marker = ["o", "v", "+", "s"]  # marker

    for index, dt_path in enumerate(dt_paths):
        print("handling {} prlines...".format(labels[index]))
        gt_dic, dt_list, gt_num = prepare_gt_and_dt(gt_path, dt_path, c_id)
        run_match(dt_list, gt_dic, mode=mode)
        recalls, precisions, scores = get_recalls_and_precisions(dt_list, gt_num, mode=mode)
        plt.plot(recalls, precisions, linewidth=0.8, color=colors[index], label=labels[index])
        indics = get_thres_index(scores, score_thres)
        for i, num in enumerate(indics):
            plt.scatter(recalls[num], precisions[num], c=colors[index], linewidths=1, marker=score_marker[i])

    start_pos = (5, 75)
    for i, score in enumerate(score_thres):
        plt.text(start_pos[0], start_pos[1]-2*i, "score: {} --> {}".format(score, score_marker[i]))
    plt.legend()
    plt.xlabel("recalls")
    plt.ylabel("precisions")
    title = c_labels[c_id] if c_id in c_labels else "unknown"
    des_saved = "./prlines_{}_test_{}.png".format(title, benchmark)
    plt.title("{} {} on {}".format(title, mode, benchmark))
    plt.savefig(des_saved)
    plt.show()
    print("done")
