import torch
import clip
from PIL import Image

import argparse
import re
import json


class Model():
    def __init__(self, model: str, similarity: str, device="cpu") -> None:
        # set the device and init the model
        self.device = device
        self.model, self.preprocess = clip.load(model, device=device)
        
        # set our similarity function
        match similarity:
            case 'cosine':
                self.sim_func = torch.nn.functional.cosine_similarity
            case 'euclidean':
                self.sim_func = lambda x, y : torch.cdist(x[:, None], y[:, None].T)

    @torch.no_grad()
    def create_prototype(self, queries: list[str]) -> torch.TensorType:
        # tokenize and encode each query separately
        tokens = [
            clip.tokenize(query)
            for query in queries
        ]
        encodings = [
            self.model.encode_text(token)
            for token in tokens
        ]
        # concatenate the query encodings
        prototype = torch.cat(encodings, dim=0) # Q x F
        # sum them together
        prototype = torch.sum(prototype, dim=0) # 1 x F
        # average them out
        prototype = prototype / len(queries)
        return prototype
    
    @torch.no_grad()
    def create_index(self, image_names: list[str]):
        images = []
        # start indexing images
        for name in image_names:
            # load image as tensor
            image = self.preprocess(Image.open(name)).unsqueeze(0).to(self.device)
            image_features = self.model.encode_image(image)
            images += [image_features]
        self.index = torch.cat(images)
    
    @torch.no_grad()
    def query_index(
        self,
        query: torch.TensorType
    ) -> torch.TensorType:
        # get the cosine sim of the query over our index
        sim = self.sim_func(self.index, query)
        return sim

def parse_args():
    parser = argparse.ArgumentParser()

    # ----- Required
    parser.add_argument(
        '-q', '--query',
        nargs='+',
        help='The query to search the given images for'
    )
    parser.add_argument(
        '-f', '--files',
        nargs='+',
        help='The image files to index and search'
    )

    # Test
    parser.add_argument(
        '-t', '--test',
        required=False,
        action='store_true',
        help='Test each function'
    )

    # ----- Optional

    # Model Hyperparameters
    parser.add_argument(
        '-m', '--model',
        required=False,
        nargs=1,
        type=str,
        choices=clip.available_models(),
        help='Set which model to use',
        default="RN50"
    )
    parser.add_argument(
        '-d', '--device',
        required=False,
        default='cpu',
        nargs=1,
        type=str,
        choices=['cpu', 'gpu'],
        help='Set the device for the model to run on'
    )
    parser.add_argument(
        '-s', '--similarity',
        required=False,
        default='cosine',
        type=str,
        choices=['cosine', 'euclidean'],
        help='Which similarity method to query with',
    )

    parser.add_argument(
        '-i', '--interactive',
        required=False,
        action='store_true',
        help='Start script in interactive mode to repeatedly query the index'
    )

    return parser.parse_args()
    
    

if __name__ == '__main__':

    # Parse arguments and flags
    args = parse_args()

    # Test our model
    if args.test:
        print("Initializing model...")
        model = Model(args.model)
        
        print("Creating index...")
        print("Files:")
        for f in args.files:
            print(f)
        model.create_index(args.files)
        
        print("Creating Query Prototype...")
        query = model.create_prototype(args.query)

        print("Querying Files")
        results = model.query_index(query)

        exit(0)

    # Initialize our model
    model = Model(
        model=args.model,
        similarity=args.similarity,
        device=args.device
    )

    # Create our index
    model.create_index(args.files)

    # Enter into a querying loop if the interactive flag is set
    if args.interactive:
        cleaner = re.compile(r'""')
        # Get our query, quit if need be
        while (q := input()) != 'quit':
            # clean the input by splitting
            queries = q.split(' ')
            queries = [
                query.replace('"', '')
                for query in queries
            ]

            # Query over the index and return the results
            query_prototype = model.create_prototype([q])
            results = model.query_index(query_prototype)
            result_dict = {
                name:score.item() for name, score in zip(args.files, results)
            }
            print(json.dumps(result_dict))

    
    # Query index with the supplied query and exit
    else:
        query = model.create_prototype(args.query)
        results = model.query_index(query)
        print(results)
        result_dict = {
            name:score.item() for name, score in zip(args.files, results)
        }
        print(json.dumps(result_dict))
    
