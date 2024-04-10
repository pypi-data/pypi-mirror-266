from pathlib import Path

from haplo.nicer_dataset import NicerDataset


def main():
    dataset_path = Path('data_nobackup/640m_parameters_and_phase_amplitudes.db')
    dataset = NicerDataset.new(dataset_path=dataset_path)

    example0 = dataset[0]
    parameters0, phase_amplitudes0 = example0
    print(parameters0)
    print(phase_amplitudes0)


if __name__ == '__main__':
    main()
