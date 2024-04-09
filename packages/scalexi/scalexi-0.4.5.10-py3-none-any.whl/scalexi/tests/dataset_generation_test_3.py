import unittest
import os
import pandas as pd
import json
from unittest.mock import patch
from scalexi.dataset_generation.prompt_completion import (
    format_prompt_completion,
    format_prompt_completion_df,
    df_to_json,
    list_to_csv,
    df_to_csv,
    parse_and_save_json,
    generate_user_prompt,
    generate_prompt_completions
)

class TestDatasetGeneration(unittest.TestCase):

    def setUp(self):
        self.prompt = "What is the capital of France?"
        self.completion = "The capital of France is Paris."
        self.start_sequence = "\n\n###\n\n"
        self.end_sequence = "END"

        self.data_list = [{'Prompt': self.prompt, 'Completion': self.completion}]
        self.output_csv = 'test_output.csv'
        self.output_json = 'test_output.json'

        if os.path.exists(self.output_csv):
            os.remove(self.output_csv)
        if os.path.exists(self.output_json):
            os.remove(self.output_json)

    def test_format_prompt_completion(self):
        result = format_prompt_completion(self.prompt, self.completion)
        expected = {
            "prompt": self.prompt.strip() + self.start_sequence,
            "completion": self.completion.strip() + self.end_sequence
        }
        self.assertEqual(result, expected)

    def test_format_prompt_completion_df(self):
        result_df = format_prompt_completion_df(self.prompt, self.completion)
        expected_df = pd.DataFrame({
            "formatted_prompt": [self.prompt.strip() + self.start_sequence],
            "formatted_completion": [self.completion.strip() + self.end_sequence]
        })
        pd.testing.assert_frame_equal(result_df, expected_df)

    def test_df_to_json(self):
        df = pd.DataFrame(self.data_list)
        df_to_json(df, self.output_json)
        self.assertTrue(os.path.exists(self.output_json))

        with open(self.output_json, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, self.data_list)

    def test_list_to_csv(self):
        list_to_csv(self.data_list, self.output_csv)
        self.assertTrue(os.path.exists(self.output_csv))

        read_df = pd.read_csv(self.output_csv)
        expected_df = pd.DataFrame(self.data_list)
        pd.testing.assert_frame_equal(read_df, expected_df)

    def test_df_to_csv(self):
        df = pd.DataFrame(self.data_list)
        df_to_csv(df, self.output_csv)
        self.assertTrue(os.path.exists(self.output_csv))

        read_df = pd.read_csv(self.output_csv)
        pd.testing.assert_frame_equal(read_df, df)

    def test_parse_and_save_json(self):
        json_str = json.dumps(self.data_list)
        parse_and_save_json(json_str, self.output_json)
        self.assertTrue(os.path.exists(self.output_json))

        with open(self.output_json, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, self.data_list)

    def test_generate_user_prompt(self):
        num_questions = 2
        question_type = "open-ended"
        result = generate_user_prompt(num_questions, question_type)
        self.assertIn("What is the capital of France?", result)
        self.assertIn("How does photosynthesis work?", result)

    @patch('scalexi.dataset_generation.prompt_completion.openai')
    def test_generate_prompt_completions(self, mock_openai):
        # Mock the OpenAI API response
        mock_openai.ChatCompletion.create.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps(self.data_list)
                }
            }]
        }
        context_text = "Provide an example context."
        output_csv = "test_output.csv"
        result = generate_prompt_completions(context_text, output_csv)
        self.assertTrue(os.path.exists(output_csv))

        with open(output_csv, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.assertEqual(row['Prompt'], self.prompt)
                self.assertEqual(row['Completion'], self.completion)

if __name__ == '__main__':
    unittest.main()
