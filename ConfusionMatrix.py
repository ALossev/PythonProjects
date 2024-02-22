def confusionmatrix(actual, predicted, labels):
    num_labels = len(labels)
    confusion_mat = [[0 for  in range(numlabels)] for  in range(num_labels)]
    label_dict = {label: index for index, label in enumerate(labels)}
    for index in range(len(actual)):
        i = label_dict[actual[index]]
        j = label_dict[predicted[index]]
        confusion_mat[i][j] += 1
    for index, label in enumerate(labels):
        i = label_dict[label]
        j = label_dict[label]
        column_sum = sum(row[i] for row in confusion_mat)
        row_sum = sum(confusion_mat[j])
        print(f"Precision for {label} :{confusion_mat[i][j]}/
{column_sum} = {confusion_mat[i][j]/ column_sum}")
        print(f"Recall for {label} :{confusion_mat[i][j]}/ {row_sum} =
{confusion_mat[i][j]/ row_sum}")
    total=0
    truePositive=0
    for index, label in enumerate(labels):
        i = label_dict[label]
        j = label_dict[label]
        truePositive+=confusion_mat[i][j]
        total+= sum(confusion_mat[j])
    print(f"Accuracy: {truePositive}/ {total} = {truePositive/ total}")
    return confusion_mat
