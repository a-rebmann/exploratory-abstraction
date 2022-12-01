import os
import random
import sys
from copy import deepcopy
from statistics import mean

import numpy as np
import pandas as pd
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter

from const import *


dirname = os.path.dirname(__file__)

path_to_files = os.path.join(dirname, 'input')
log_dir = 'uilogs'


def prepeare_log(log_name, parse_dates=False):
    if ".xes" in log_name:
        log1 = xes_importer.apply(os.path.join(path_to_files, log_dir, log_name))
        df = log_converter.apply(log1, variant=log_converter.Variants.TO_DATA_FRAME)
        df = df.reset_index()
    else:
        df = pd.read_csv(path_to_files + "/" + log_dir + "/" + log_name, sep=",", quotechar='"', engine="python",
                         error_bad_lines=False, parse_dates=parse_dates)
    return df


def load_and_convert_to_df(log):
    return log_converter.apply(log, variant=log_converter.Variants.TO_DATA_FRAME)


def buildMergedLogAgostinelli(num_of_logs=10):
    for num_of_log in range(num_of_logs):
        log1 = xes_importer.apply(os.path.join(path_to_files, log_dir + "/Leno", "log3.xes"))
        log2 = xes_importer.apply(os.path.join(path_to_files, log_dir + "/Agostinelli", "agostinelli.xes"))
        df1 = log_converter.apply(log1, variant=log_converter.Variants.TO_DATA_FRAME)
        df1.rename(
            columns={"FileName": "target.workbookName", "Sheet": "target.sheetName", "time:timestamp": "timeStamp",
                     "source": "targetApp", "concept:name": "eventType", "Url": "url", "Value": "target.value",
                     "Label": "target.innerText", "tag_checked": "target.checked"}, inplace=True)
        df1["target.id"] = df1["Column"] + df1["Row"]
        df1.drop('Row', axis=1, inplace=True)
        df1.drop('Column', axis=1, inplace=True)
        df1.drop('case:description', axis=1, inplace=True)
        df1.drop('lifecycle:transition', axis=1, inplace=True)

        df1['targetApp'] = df1['targetApp'].map({'Web': 'Chrome', 'Excel': 'Excel'})

        # Agostinelli

        df4 = log_converter.apply(log2, variant=log_converter.Variants.TO_DATA_FRAME)
        mask = df4['tag_value'] == ""
        df4['tag_value'] = np.where(df4['tag_value'].isnull() | mask, df4['clipboard_content'],
                                    df4['tag_value'])
        df4['tag_value'] = np.where(df4['tag_value'].isnull(), df4['cell_content'],
                                    df4['tag_value'])
        df4['tag_name'] = df4['tag_name'] + df4['xpath']

        df4.rename(
            columns={"time:timestamp": "timeStamp",
                     "application": "targetApp", "concept:name": "eventType", "browser_url": "url", "id": "target.name",
                     # "clipboard_content": "target.value",
                     "tag_category": "target.tagName",
                     "org:resource": "userID",
                     "workbook": "target.workbookName",
                     "current_worksheet": "target.sheetName",
                     "tag_value": "target.value",
                     "tag_name": "target.innerText"}, inplace=True)
        # df4["target.id"] = df1["Column"] + df1["Row"]
        df4.drop('description', axis=1, inplace=True)
        df4.drop('case:creator', axis=1, inplace=True)
        df4.drop('xpath', axis=1, inplace=True)
        df4.drop('cell_range', axis=1, inplace=True)
        df4.drop('cell_range_number', axis=1, inplace=True)
        df4.drop('window_size', axis=1, inplace=True)
        df4.drop('slides', axis=1, inplace=True)
        df4.drop('effect', axis=1, inplace=True)
        df4.drop('hotkey', axis=1, inplace=True)
        df4.drop('newZoomFactor', axis=1, inplace=True)
        df4.drop('oldZoomFactor', axis=1, inplace=True)
        df4.drop('window_ingognito', axis=1, inplace=True)
        df4.drop('file_size', axis=1, inplace=True)
        df4.drop('tag_title', axis=1, inplace=True)
        df4.drop('tag_html', axis=1, inplace=True)
        df4.drop('tag_href', axis=1, inplace=True)
        df4.drop('xpath_full', axis=1, inplace=True)
        df4.drop('title', axis=1, inplace=True)
        df4.drop('eventQual', axis=1, inplace=True)
        df4.drop('tag_option', axis=1, inplace=True)
        df4.drop('tag_attributes', axis=1, inplace=True)
        # df4.drop('tag_checked', axis=1, inplace=True)
        df4.drop('lifecycle:transition', axis=1, inplace=True)
        df4.drop('event_src_path', axis=1, inplace=True)
        df4.drop('event_dest_path', axis=1, inplace=True)
        df4.drop('mouse_coord', axis=1, inplace=True)
        to_rem = []
        for col in df4.columns:
            if "tab" in col:
                to_rem.append(col)
        for col in to_rem:
            df4.drop(col, axis=1, inplace=True)

        df1['targetApp'] = df1['targetApp'].map({'Web': 'Chrome', 'Excel': 'Excel'})

        df2 = pd.read_csv(path_to_files + "/" + log_dir + "/Leno" + "/" + "Reimbursement_segmented.csv", sep=",",
                          quotechar='"',
                          engine="python", error_bad_lines=False)
        df3 = pd.read_csv(path_to_files + "/" + log_dir + "/Leno" + "/" + "StudentRecord_segmented.csv", sep=",",
                          quotechar='"',
                          engine="python", error_bad_lines=False)

        df1[LABEL] = "CopyPasteStuff"
        df2[LABEL] = "Reimbursement"
        df3[LABEL] = "StudentRecord"
        df4[LABEL] = "TravelRequest"

        df1[INDEX] = 0
        df2[INDEX] = 0
        df3[INDEX] = 0
        df4[INDEX] = 0

        log1_segments = []
        log2_segments = []
        log3_segments = []
        log4_segments = []

        current_log1_seg = []
        current_log2_seg = []
        current_log3_seg = []
        current_log4_seg = []

        log1_prev = None
        idx = 0
        for index, row in df1.iterrows():

            if log1_prev is not None and row["case:concept:name"] != log1_prev:
                log1_segments.append(current_log1_seg)
                current_log1_seg = []
                idx += 1
            row[INDEX] = idx
            log1_prev = row["case:concept:name"]
            current_log1_seg.append(row)
        log1_segments.append(current_log1_seg)

        log4_prev = None
        idx = 0
        # Duplicates segments in the log
        duplication = 20
        for index, row in df4.iterrows():

            if log4_prev is not None and row["case:concept:name"] != log4_prev:
                for i in range(duplication):
                    seg = []
                    for row1 in current_log4_seg:
                        row_c = deepcopy(row1)
                        row_c[INDEX] = i + idx * 100
                        seg.append(row_c)
                    log4_segments.append(seg)
                current_log4_seg = []
                idx += 1
            # row[INDEX] = idx
            log4_prev = row["case:concept:name"]
            current_log4_seg.append(row)
        for i in range(duplication):
            seg = []
            for row1 in current_log4_seg:
                row_c = deepcopy(row1)
                row_c[INDEX] = i + idx * 100
                seg.append(row_c)
            log4_segments.append(seg)

        log2_prev = None
        idx = 0
        for index, row in df2.iterrows():
            if log2_prev is not None and log2_prev != row["caseID"]:
                log2_segments.append(current_log2_seg)
                current_log2_seg = []
                idx += 1
            row[INDEX] = idx
            log2_prev = row["caseID"]
            current_log2_seg.append(row)
        log2_segments.append(current_log2_seg)
        log3_prev = None
        idx = 0
        for index, row in df3.iterrows():

            if log3_prev is not None and log3_prev != row["caseID"]:
                log3_segments.append(current_log3_seg)
                current_log3_seg = []
                idx += 1
            row[INDEX] = idx
            log3_prev = row["caseID"]
            current_log3_seg.append(row)
        log3_segments.append(current_log3_seg)
        print(len(log1_segments), len(log2_segments), len(log3_segments), len(log4_segments))

        mergedDF = pd.DataFrame()
        if len(log1_segments) > 100:
            log1_segments = random.sample(log1_segments, k=100)
        all_segs = log1_segments + log2_segments + log3_segments + log4_segments
        random.shuffle(all_segs)
        for seg in all_segs:
            new_df = pd.DataFrame(seg)
            #print(new_df.columns)
            #print(mergedDF.columns)
            mergedDF = pd.concat([mergedDF, new_df], sort=False, ignore_index=True).fillna("")
            # mergedDF = mergedDF.reset_index(drop=True)
        mergedDF.drop('case:concept:name', axis=1, inplace=True)
        mergedDF.drop('caseID', axis=1, inplace=True)
        mergedDF.to_csv(path_to_files + "/" + log_dir + "/" + "L2_" + str(num_of_log + 10) + ".csv")
        sys.exit(0)


def buildMergedLogLeno(num_of_logs=10):
    for num_of_log in range(num_of_logs):
        log1 = xes_importer.apply(os.path.join(path_to_files, log_dir + "/Leno", "log3.xes"))
        df1 = log_converter.apply(log1, variant=log_converter.Variants.TO_DATA_FRAME)
        df1.rename(
            columns={"FileName": "target.workbookName", "Sheet": "target.sheetName", "time:timestamp": "timeStamp",
                     "source": "targetApp", "concept:name": "eventType", "Url": "url", "Value": "target.value",
                     "Label": "target.innerText"}, inplace=True)
        df1["target.id"] = df1["Column"] + df1["Row"]
        df1.drop('Row', axis=1, inplace=True)
        df1.drop('Column', axis=1, inplace=True)
        df1.drop('case:description', axis=1, inplace=True)
        df1.drop('lifecycle:transition', axis=1, inplace=True)

        df1['targetApp'] = df1['targetApp'].map({'Web': 'Chrome', 'Excel': 'Excel'})

        df2 = pd.read_csv(path_to_files + "/" + log_dir + "/Leno" + "/" + "Reimbursement_segmented.csv", sep=",",
                          quotechar='"',
                          engine="python", error_bad_lines=False)
        df3 = pd.read_csv(path_to_files + "/" + log_dir + "/Leno" + "/" + "StudentRecord_segmented.csv", sep=",",
                          quotechar='"',
                          engine="python", error_bad_lines=False)

        df1[LABEL] = "CopyPasteStuff"
        df2[LABEL] = "Reimbursement"
        df3[LABEL] = "StudentRecord"

        df1[INDEX] = 0
        df2[INDEX] = 0
        df3[INDEX] = 0

        log1_segments = []
        log2_segments = []
        log3_segments = []

        current_log1_seg = []
        current_log2_seg = []
        current_log3_seg = []

        log1_prev = None
        idx = 0
        for index, row in df1.iterrows():
            if log1_prev is not None and row["case:concept:name"] != log1_prev:
                log1_segments.append(current_log1_seg)
                current_log1_seg = []
                idx += 1
            row[INDEX] = idx
            log1_prev = row["case:concept:name"]
            current_log1_seg.append(row)
        log1_segments.append(current_log1_seg)
        log2_prev = None
        idx = 0
        for index, row in df2.iterrows():
            if log2_prev is not None and log2_prev != row["caseID"]:
                log2_segments.append(current_log2_seg)
                current_log2_seg = []
                idx += 1
            row[INDEX] = idx
            log2_prev = row["caseID"]
            current_log2_seg.append(row)
        log2_segments.append(current_log2_seg)
        log3_prev = None
        idx = 0
        for index, row in df3.iterrows():
            if log3_prev is not None and log3_prev != row["caseID"]:
                log3_segments.append(current_log3_seg)
                current_log3_seg = []
                idx += 1
            row[INDEX] = idx
            log3_prev = row["caseID"]
            current_log3_seg.append(row)
        log3_segments.append(current_log3_seg)


        mergedDF = pd.DataFrame()
        if len(log1_segments) > 100:
            log1_segments = random.sample(log1_segments, k=100)
        print(len(log1_segments), len(log2_segments), len(log3_segments))
        all_segs = log1_segments + log2_segments + log3_segments
        random.shuffle(all_segs)
        for seg in all_segs:
            mergedDF = pd.concat([mergedDF, pd.DataFrame(seg)], sort=False, ignore_index=True).fillna("")
        mergedDF.drop('case:concept:name', axis=1, inplace=True)
        mergedDF.drop('caseID', axis=1, inplace=True)
        mergedDF.drop('user', axis=1, inplace=True)
        mergedDF.to_csv(path_to_files + "/" + log_dir + "/" + "L1_" + str(num_of_log + 1) + ".csv")
        sys.exit(0)


# inserts up to three duplicates
def randomly_insert_some_noise(new_seg):
    number_of_duplicates = random.choice(range(1, 4))
    for _ in range(number_of_duplicates):
        to_duplicate = random.choice(range(1, len(new_seg)-1))
        duplicate = deepcopy(new_seg[to_duplicate])
        new_seg.insert(to_duplicate, duplicate)
    return new_seg


def buildMergedLogLuka(num_of_logs=10):
    all_segs = []
    idx = 1
    for (dir_path, dir_names, filenames) in os.walk(path_to_files + "/" + log_dir + "/Luka"):
        for filename in filenames:

            if not any(to_consider in filename for to_consider in ["TF_02", "TF_03", "TF_13", "TF_04"]):
                 continue
            print(filename)
            seg = []
            df = pd.read_csv(path_to_files + "/" + log_dir + "/Luka" + "/" + filename, sep=",",
                             quotechar='"',
                             engine="python", error_bad_lines=False)
            df.columns = ['case', 'eventType', 'target.id', 'target.css', 'timeStamp', 'target.value', 'x', 'y', 'target.tagName', 'target.name']
            for index, row in df.iterrows():
                if row['case'] == 0:
                     continue
                if row['case'] != 2 and "TF_02" in filename:
                    continue
                if row['case'] != 3 and "TF_03" in filename:
                    continue
                if row['case'] != 3 and "TF_13" in filename:
                    continue
                if row['case'] != 4 and "TF_04" in filename:
                    continue
                row[INDEX] = idx
                row[LABEL] = filename #+ str(row['case'])
                seg.append(row)
            all_segs.append(seg)
            idx += 1
            if idx == 7:
                break
    print(len(all_segs))
    duplicates = []
    for seg in all_segs:
        for i in range(29):
            new_seg = deepcopy(seg)
            for row in new_seg:
                row[INDEX] = i*100 + row[INDEX]
            randomly_insert_some_noise(new_seg)
            duplicates.append(new_seg)
    for elm in duplicates:
        all_segs.append(elm)
    for num_of_log in range(num_of_logs):
        mergedDF = pd.DataFrame()
        random.shuffle(all_segs)
        for seg in all_segs:
            mergedDF = pd.concat([mergedDF, pd.DataFrame(seg)], sort=False, ignore_index=True).fillna("")
        mergedDF['targetApp'] = "Fiori"
        mergedDF['target.workbookName'] = ""
        mergedDF['target.sheetName'] = ""
        mergedDF['url'] = ""
        mergedDF.drop('case', axis=1, inplace=True)
        mergedDF['content'] = ""
        mergedDF['target.innerText'] = mergedDF['target.name']
        mergedDF.to_csv(path_to_files + "/" + log_dir + "/" + "L3" + str(num_of_log + 1) + ".csv")
        sys.exit(0)


def get_average_task_length():
    for (dir_path, dir_names, filenames) in os.walk(path_to_files + "/" + log_dir):
        timediffs_overall = []
        for filename in filenames:
            print(filename)
            df = prepeare_log(filename, parse_dates=True)
            vals = []
            for name, group in df.groupby([LABEL, INDEX]):
                vals.extend(list((group['timeStamp'] - group['timeStamp'].shift()).fillna(
                    pd.Timedelta('0 days'))))
            print(mean(val.total_seconds() for val in vals))
            timediffs_overall.extend(vals)
        print("avg trans. time", mean(val.total_seconds() for val in timediffs_overall))

                #df['json'].to_csv(os.path.join(output_dir, "json", filename+"json.txt"), index=False, encoding='utf-8')

###################################
# Uncomment the first line below to create random evaluation logs based on available task data
# Uncomment the second line below to create JSON events, such as those streamed to Kafka
###################################
buildMergedLogAgostinelli(num_of_logs=1)




