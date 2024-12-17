import os
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from tqdm import tqdm
from scipy.spatial.distance import cosine
from sklearn.metrics import mean_squared_error

# ==========================
# Classification Performance 분석
# ==========================
def evaluate_classification_results(results_csv, label_file):
    print("\n=== Classification Performance ===")
    # 결과 파일 및 Ground Truth 라벨 불러오기
    results_df = pd.read_csv(results_csv)
    labels_df = pd.read_csv(label_file)

    # Ground Truth 라벨 매핑
    video_to_label = dict(zip(labels_df['video_id'], labels_df['encoded_label']))
    results_df['ground_truth'] = results_df['video_file'].apply(lambda x: video_to_label.get(x.replace('.npy', ''), -1))

    # 유효한 데이터만 필터링
    valid_results = results_df[results_df['ground_truth'] != -1]
    if valid_results.empty:
        print("Error: No valid ground truth labels found.")
        return

    # 성능 평가
    y_true = valid_results['ground_truth'].values
    y_pred = valid_results['predicted_class'].values

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-Score: {f1:.4f}")

# ==========================
# Reconstruction Performance 분석
# ==========================
def evaluate_reconstruction(reconstructed_dir, ground_truth_dir):
    print("\n=== Reconstruction Performance ===")
    mse_scores = []
    cosine_similarities = []

    # Ground Truth 경로 매핑 (순회 탐색)
    ground_truth_files = {}
    for root, _, files in os.walk(ground_truth_dir):
        for file in files:
            if file.endswith('.npy'):
                ground_truth_files[file] = os.path.join(root, file)

    # 재구성된 오디오 피처 순회
    for rec_file in tqdm(os.listdir(reconstructed_dir), desc="Evaluating Reconstruction"):
        if rec_file.startswith('reconstructed_') and rec_file.endswith('.npy'):
            # 파일명에서 'reconstructed_' 제거
            original_file = rec_file.replace('reconstructed_', '')
            
            if original_file in ground_truth_files:
                # 재구성된 피처와 Ground Truth 피처 불러오기
                rec_path = os.path.join(reconstructed_dir, rec_file)
                gt_path = ground_truth_files[original_file]

                rec_feat = np.load(rec_path)
                gt_feat = np.load(gt_path)

                # MSE 및 Cosine Similarity 계산
                mse = mean_squared_error(gt_feat.flatten(), rec_feat.flatten())
                cosine_sim = 1 - cosine(gt_feat.flatten(), rec_feat.flatten())  # Cosine Similarity

                mse_scores.append(mse)
                cosine_similarities.append(cosine_sim)

    # 평균 성능 출력
    if mse_scores and cosine_similarities:
        print(f"Average MSE: {np.mean(mse_scores):.4f}")
        print(f"Average Cosine Similarity: {np.mean(cosine_similarities):.4f}")
    else:
        print("Error: No matching reconstructed and ground truth audio features found.")

# ==========================
# Main 분석 코드
# ==========================
if __name__ == "__main__":
    # 경로 설정
    classification_results_csv = r"C:/Users/swu/Desktop/AudioFeatureGeneration/Audio-Feature-Generation/data/classification_results.csv"
    ground_truth_labels_csv = r"C:/Users/swu/Desktop/AudioFeatureGeneration/lstm_labels.csv"
    reconstructed_audio_dir = r"C:/Users/swu/Desktop/AudioFeatureGeneration/Audio-Feature-Generation/data/reconstructed-audio"
    ground_truth_audio_dir = r"C:/Users/swu/Desktop/AudioFeatureGeneration/Audio-Feature-Generation/data/audio-features"

    # Classification 분석
    evaluate_classification_results(classification_results_csv, ground_truth_labels_csv)

    # Reconstruction 분석
    evaluate_reconstruction(reconstructed_audio_dir, ground_truth_audio_dir)