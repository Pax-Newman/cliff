import socket
import torch
from PIL import Image

import clip

class Server():
    """ Handles operating the CLIP model over a simple sockets based API """

    def __init__(
            self,
            address: str,       # ip address of server
            port: int,          # port of the server
            model: str,         # which model to use
            similarity: str,    # similarity function
            ) -> None:
        # bind our socket
        self.sock = socket.socket()
        self.sock.bind((address, port))

        # grab the socket's port #
        self.port = self.sock.getsockname()[1]

        self.vectorizedIndex: torch.Tensor
        self.pathIndex: list[str] = []

        # init the model and tokenizer
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = torch.hub.load("openai/CLIP", model, device=self.device)
        self.tokenize = torch.hub.load("openai/CLIP", "tokenize")

        match similarity:
            case 'cosine':
                self.sim_func = torch.nn.functional.cosine_similarity
            case 'euclidean':
                self.sim_func = lambda x, y : torch.cdist(x[:, None], y[:, None].T)

    @torch.no_grad()
    def __embed_file(self, filepath: str) -> torch.Tensor:
        """ Embeds a file's contents into a vector using CLIP """
        image_types = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')
        # Process image
        if filepath.lower().endswith(image_types):
            image_file = Image.open(filepath)
            return self.preprocess(image_file).unsqueeze(0).to(self.device)
        # Process text
        else:
            with open(filepath) as f:
                return self.tokenize(f.read())

    def add_to_index(self, *filepaths: str):
        """ Add a set of files to the search index """
        images = [
                self.__embed_file(path)
                for path in filepaths
                ]
       
        # Turn our embedded images into a single tensor
        new_images = torch.cat(images)
        # Add that tensor to our main index
        if self.vectorizedIndex:
            self.vectorizedIndex = torch.cat((self.vectorizedIndex, new_images))
        else:
            self.vectorizedIndex = torch.cat(images)
        # Add the file names to our index of file paths
        self.pathIndex += filepaths

    @torch.no_grad()
    def build_prototype(self, queries: list[torch.Tensor]):
        """ Builds a prototype out of a list of tensors """
        
        # Concatenate our query vectors into a single tensor
        gathered_queries = torch.cat(queries, dim=0)

        # Average the queries into a single prototype
        prototype = gathered_queries.sum(dim=0) / len(queries)
        return prototype

    @torch.no_grad()
    def query(self, prototype: torch.Tensor) -> list[str]:
        """
        Queries the index with a given prototype query.
        Returns a list of paths sorted by the similarity score of the query
        """
        
        sim = self.sim_func(self.vectorizedIndex, prototype)
        
        sorted_paths = [
                # grab only the paths from the resulting sorted list
                path for _, path in sorted(
                    # enumerate the list so we can access the similarity scores by index
                    enumerate(self.pathIndex),
                    # sort by the similarity value
                    key=lambda index_path : sim[index_path[0]].item()
                    )
                ]

        return sorted_paths
    
    def close(self):
        """ Shutdown the server """
        ...


if __name__ == '__main__':
    # port 0 will allow the OS to self select a safe port for us
    address, port = '', 0

    server = Server(address, port)

    # Display the server information 
    print(server.sock.getsockname())


