def retrieve_top_hyper(study):
    """
    Truy xuất các hyperparameter hàng đầu từ một đối tượng Optuna Study.

    Args:
    study (optuna.study.Study): Đối tượng Optuna Study.

    Returns:
    list: Danh sách chứa các hyperparameter hàng đầu.
    """
    # Truy xuất tất cả các thử nghiệm
    trials = study.trials

    # Sắp xếp các thử nghiệm dựa trên các giá trị mục tiêu
    trials.sort(key=lambda trial: trial.values, reverse=True)

    # Lấy ra 100 thử nghiệm hàng đầu
    top_trials = trials[:100]

    # Trích xuất các hyperparameter từ các thử nghiệm hàng đầu
    top_hyperparameters = [trial.params for trial in top_trials]

    return top_hyperparameters
