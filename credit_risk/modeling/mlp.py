import torch
import torch.nn as nn
import numpy as np
from typing import Union
from torch.utils.data import DataLoader, TensorDataset


class MLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: list[int] = [128, 64], dropout: float = 0.2):
        super().__init__()
        layers = []
        prev_dim = input_dim
        for h in hidden_dim:
            layers.append(nn.Linear(prev_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_dim = h
            
        layers.append(nn.Linear(prev_dim, 1))
        self.net = nn.Sequential(*layers)
        
    def forward(self, x):
        return self.net(x).squeeze(-1)
    

def train_one_fold(X_train: np.array, y_train: np.array, X_val: np.array, n_epochs: int = 20, batch_size: int = 2048):
    """Train the MLP for one fold"""
    
    X_train_t = torch.from_numpy(X_train.astype(np.float32))
    y_train_t = torch.from_numpy(y_train.astype(np.float32))
    X_val_t = torch.from_numpy(X_val.astype(np.float32))
    
    model = MLP(input_dim=X_train.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.BCEWithLogitsLoss()
    
    dataset = TensorDataset(X_train_t, y_train_t)
    loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)
    
    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0
        
        for xb, yb in loader:
            optimizer.zero_grad()
            logits = model(xb)
            loss = loss_fn(logits, yb)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        # print(f"Epoch {epoch}: loss={epoch_loss/len(loader):.4f}")
        
    # predict
    model.eval()
    with torch.no_grad():
        val_logits = model(X_val_t)
        val_proba = torch.sigmoid(val_logits).numpy()
        
    return val_proba

def train_nn(X_train: np.array, y_train: np.array, n_epochs: int = 20, dropout: float = 0.2, batch_size: int = 2048, hidden_dim: list[int] = [128, 64]) -> Union[MLP, list[float]]:
    """trains the MLP model"""
    X_train_t = torch.from_numpy(X_train.astype(np.float32))
    y_train_t = torch.from_numpy(y_train.astype(np.float32))
    
    model = MLP(input_dim=X_train.shape[1], hidden_dim=hidden_dim, dropout=dropout)
    cost_fn = nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    dataset = TensorDataset(X_train_t, y_train_t)
    loader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True)
    
    loss_track = []
    for epoch in range(n_epochs):
        epoch_cost = 0
        
        for xb, yb in loader:
            optimizer.zero_grad()
            
            # forward
            logits = model(xb)
            loss = cost_fn(logits, yb)
            
            # backward
            loss.backward()
            optimizer.step()
            epoch_cost += loss.item()
            
        loss_track.append(epoch_cost/len(loader))
        print(f"{epoch+1} epoch: avg loss per batch - {epoch_cost/len(loader)}")
        
    return model, loss_track