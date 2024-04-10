import logging
from lamini.evaluators.custom.ecommerce_evaluator import EcommerceEvaluator
from lamini.evaluators.custom.earnings_call_evaluator import EarningsCallEvaluator
from lamini.evaluators.custom.icd_evaluator import ICDEvaluator
from lamini.evaluators.utils.utils import format_results

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CustomEvaluator:
    def __init__(
        self,
        model,
        task_names=None,
        max_examples=2,
        shopping_dataset_path="lamini/evaluators/custom/datasets/shopping.jsonl",
        earnings_dataset_path="lamini/evaluators/custom/datasets/earnings_calls.jsonl",
        icd_dataset_path="lamini/evaluators/custom/datasets/icd11.jsonl",
    ):
        """
        Initializes the Evaluator with the given model and settings.
        """
        if task_names is None:
            self.task_names = ["products", "earnings", "icd11"]
        else:
            self.task_names = task_names
        self.model = model
        self.max_examples = max_examples
        self.shopping_dataset_path = shopping_dataset_path
        self.earnings_dataset_path = earnings_dataset_path
        self.icd_dataset_path = icd_dataset_path

    async def evaluate(self):
        """
        Performs the evaluation process by computing scores.

        Returns:
            dict: A dictionary containing evaluation results.
        """
        try:
            model_type = "lamini"
            ecommerce_results, earnings_results, icd_results = {}, {}, {}
            if "products" in self.task_names:
                ecomm_eval = EcommerceEvaluator(
                    self.shopping_dataset_path,
                    model_type,
                    self.model,
                    int(self.max_examples),
                )
                ecommerce_results = await ecomm_eval.evaluate_hallucination()

            if "earnings" in self.task_names:
                earnings_eval = EarningsCallEvaluator(
                    self.earnings_dataset_path,
                    model_type,
                    self.model,
                    int(self.max_examples),
                )
                earnings_results = await earnings_eval.evaluate_hallucination()

            if "icd11" in self.task_names:
                icd_eval = ICDEvaluator(
                    self.icd_dataset_path,
                    model_type,
                    self.model,
                    int(self.max_examples),
                )
                icd_results = await icd_eval.evaluate_hallucination()

            results = format_results(
                self.model, ecommerce_results, earnings_results, icd_results
            )
            print("full results:", results)
            return results
        except Exception as e:
            logging.error(f"Error during evaluation: {e}")
            raise
