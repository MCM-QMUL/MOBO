from botorch.utils.transforms import normalize, unnormalize
from botorch.models.gp_regression import SingleTaskGP
from botorch.models.model_list_gp_regression import ModelListGP
from botorch.models.transforms.outcome import Standardize
from gpytorch.mlls.sum_marginal_log_likelihood import SumMarginalLogLikelihood
import torch

tkwargs = {"dtype": torch.double, "device": torch.device("cuda" if torch.cuda.is_available() else "cpu")}
def initialise_model(problem, train_x, train_y, kernel, NOISE_SE: None):
    
    # NOISE_SE = torch.tensor([1e-5, 1e-5], **tkwargs)
    train_x = normalize(train_x, problem.bounds)

    # treating each output to be independent, 1 model per output
    models = []
    for i in range(train_y.shape[-1]):
        # train_yvar = torch.full_like(train_y[:,i].unsqueeze(-1), NOISE_SE[i] ** 2)
        models.append(
            SingleTaskGP(train_x, 
                        train_y[:,i].unsqueeze(-1), 
              #          train_Yvar=train_yvar,
                        covar_module=kernel,
                        outcome_transform=Standardize(m=1))
        )
    model = ModelListGP(*models)
    mll = SumMarginalLogLikelihood(model.likelihood, model)

    return mll, model
