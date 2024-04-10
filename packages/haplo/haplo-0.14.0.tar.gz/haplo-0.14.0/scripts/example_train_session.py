from pathlib import Path

from torch.optim import AdamW

from haplo.distributed import distributed_logging
from haplo.losses import PlusOneBeforeUnnormalizationChiSquaredStatisticMetric, \
    PlusOneChiSquaredStatisticMetric, SumDifferenceSquaredOverMedianExpectedSquaredMetric
from haplo.models import Cura
from haplo.nicer_dataset import NicerDataset, split_dataset_into_count_datasets
from haplo.nicer_transform import PrecomputedNormalizeParameters, PrecomputedNormalizePhaseAmplitudes
from haplo.pbs_helper import schedule_self_process_interrupt_signal_before_pbs_end_time
from haplo.train_hyperparameter_configuration import TrainHyperparameterConfiguration
from haplo.train_logging_configuration import TrainLoggingConfiguration
from haplo.train_session import train_session, load_latest_state
from haplo.train_system_configuration import TrainSystemConfiguration


@distributed_logging
def example_train_session():
    full_dataset_path = Path('data/800k_parameters_and_phase_amplitudes.db')
    full_train_dataset = NicerDataset.new(
        dataset_path=full_dataset_path,
        length=600_000_000,
        parameters_transform=PrecomputedNormalizeParameters(),
        phase_amplitudes_transform=PrecomputedNormalizePhaseAmplitudes(),
        in_memory=True
    )
    test_dataset, validation_dataset, train_dataset, _ = split_dataset_into_count_datasets(
        full_train_dataset, [10_000, 10_000, 50_000])
    model = Cura()
    loss_function = SumDifferenceSquaredOverMedianExpectedSquaredMetric()
    metric_functions = [PlusOneChiSquaredStatisticMetric(), PlusOneBeforeUnnormalizationChiSquaredStatisticMetric(),
                        SumDifferenceSquaredOverMedianExpectedSquaredMetric()]
    hyperparameter_configuration = TrainHyperparameterConfiguration.new(cycles=5)
    system_configuration = TrainSystemConfiguration.new(preprocessing_processes_per_train_process=1)
    optimizer = AdamW(params=model.parameters(), lr=hyperparameter_configuration.learning_rate,
                      weight_decay=hyperparameter_configuration.weight_decay,
                      eps=hyperparameter_configuration.optimizer_epsilon)
    # load_latest_state(model, optimizer, Path('sessions/2024_03_03_10_12_25_32_node_2_gpus_1_pp_500m_qi_loss_continued'))
    run_comments = f'base_old_version'  # Whatever you want to log in a string.
    additional_log_dictionary = {
        'model_name': type(model).__name__, 'train_dataset_size': len(train_dataset), 'run_comments': run_comments
    }
    logging_configuration = TrainLoggingConfiguration.new(
        wandb_project='profiling', wandb_entity='ramjet', additional_log_dictionary=additional_log_dictionary)
    # schedule_self_process_interrupt_signal_before_pbs_end_time()
    train_session(train_dataset=train_dataset, validation_dataset=validation_dataset, model=model,
                  loss_function=loss_function, metric_functions=metric_functions, optimizer=optimizer,
                  hyperparameter_configuration=hyperparameter_configuration, system_configuration=system_configuration,
                  logging_configuration=logging_configuration)


if __name__ == '__main__':
    example_train_session()
