from fuxion.pipelines import DatasetPipeline

irp_chain = DatasetPipeline.from_template(
    generator_template="irp/generator.template",
    normalizer_template="irp/normalizer.template",
    few_shot_file="irp/irp.json",
    dataset_name="irp_dataset",
    k=3,
    model_name="HuggingFaceH4/zephyr-7b-beta",
    cache=False,
    verbose=True,
    temperature=1.0,
    # batch_save=True,
    # batch_size = 1000,
)

result = irp_chain.execute()
print(result)