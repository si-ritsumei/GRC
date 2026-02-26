#適合率・再現率・Fスコアを計算

class prf_Calculator:
    def calculate_metrics(self, true_set, predicted_set):
        """
        適合率、再現率、Fスコアを計算する。
        """
        true_positive = len(true_set.intersection(predicted_set))
        precision = true_positive / len(predicted_set) if predicted_set else 0
        recall = true_positive / len(true_set) if true_set else 0
        f_score = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0
        print(f"Precision: {precision}, Recall: {recall}, F-Score: {f_score}")
        return precision, recall, f_score

    def average_metrics(self, metrics_list):
        """
        渡されたリストから適合率、再現率、Fスコアの平均を計算する。
        """
        avg_precision = sum(m[0] for m in metrics_list) / len(metrics_list) if metrics_list else 0
        avg_recall = sum(m[1] for m in metrics_list) / len(metrics_list) if metrics_list else 0
        avg_f_score = sum(m[2] for m in metrics_list) / len(metrics_list) if metrics_list else 0
        print(f"Precision: {avg_precision}, Recall: {avg_recall}, F-Score: {avg_f_score}")
        return avg_precision, avg_recall, avg_f_score

