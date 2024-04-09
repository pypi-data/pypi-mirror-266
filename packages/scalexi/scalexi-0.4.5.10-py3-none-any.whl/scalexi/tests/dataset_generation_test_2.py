import unittest
import os
import openai
import pandas as pd
from scalexi.dataset_generation.prompt_completion import (
    format_prompt_completion,
    format_prompt_completion_df,
    generate_user_prompt,
    generate_prompt_completions,
    df_to_json,
    list_to_csv,
    df_to_csv,
)

class TestMyFunctions(unittest.TestCase):

    def test_format_prompt_completion(self):
        # Test the format_prompt_completion function
        formatted = format_prompt_completion("Prompt", "Completion")
        expected = {"prompt": "Prompt\n\n###\n\n", "completion": "CompletionEND"}
        self.assertEqual(formatted, expected)

    def test_format_prompt_completion_df(self):
        # Test the format_prompt_completion_df function
        formatted_df = format_prompt_completion_df("Prompt", "Completion")
        expected_df = pd.DataFrame({"formatted_prompt": ["Prompt\n\n###\n\n"], "formatted_completion": ["CompletionEND"]})
        pd.testing.assert_frame_equal(formatted_df, expected_df)

    def test_generate_user_prompt(self):
        # Test the generate_user_prompt function
        user_prompt = generate_user_prompt(3, "open-ended")
        self.assertTrue(user_prompt.startswith("In light of the given context, craft precisely 3 pairs"))

    def test_generate_prompt_completions(self):
        # Test the generate_prompt_completions function
        context_text = "This is a test context."
        output_csv = "test_output.csv"
        system_prompt = "System prompt."
        num_questions = 3
        question_type = "open-ended"
        completions = generate_prompt_completions(
            context_text,
            output_csv,
            system_prompt,
            user_prompt="",
            openai_key= os.environ.get("OPENAI_API_KEY"),
            num_questions=num_questions,
            question_type=question_type
        )
        
        # Check if completions were generated and saved
        self.assertTrue(os.path.isfile(output_csv))
        
        # Clean up by deleting the test CSV file
        os.remove(output_csv)

    def test_df_to_json(self):
        # Test the df_to_json function
        df = pd.DataFrame({"formatted_prompt": ["Prompt1\n\n###\n\n", "Prompt2\n\n###\n\n"], "formatted_completion": ["Completion1END", "Completion2END"]})
        json_output = "test_json_output.json"
        df_to_json(df, json_output)
        
        # Check if JSON file was saved
        self.assertTrue(os.path.isfile(json_output))
        
        # Clean up by deleting the test JSON file
        os.remove(json_output)

    def test_list_to_csv(self):
        # Test the list_to_csv function
        data_list = [{"Prompt": "Prompt1", "Completion": "Completion1"}, {"Prompt": "Prompt2", "Completion": "Completion2"}]
        output_file = "test_list_output.csv"
        list_to_csv(data_list, output_file)
        
        # Check if CSV file was saved
        self.assertTrue(os.path.isfile(output_file))
        
        # Clean up by deleting the test CSV file
        os.remove(output_file)

    def test_df_to_csv(self):
        # Test the df_to_csv function
        df = pd.DataFrame({"Prompt": ["Prompt1", "Prompt2"], "Completion": ["Completion1", "Completion2"]})
        output_file = "test_df_output.csv"
        df_to_csv(df, output_file)
        
        # Check if CSV file was saved
        self.assertTrue(os.path.isfile(output_file))
        
        # Clean up by deleting the test CSV file
        os.remove(output_file)


if __name__ == '__main__':
    unittest.main()
