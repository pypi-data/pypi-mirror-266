import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import landborn

def collides(x1,y1,x2,y2, r):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2) < 2 * r

def check_collisions(candidate_ys, collisions, x, r):
    candidate_ys = sorted(candidate_ys, key=np.abs)
    for y in candidate_ys:
        has_collision = False
        for (x_prime, y_prime) in collisions:
            if collides(x, y, x_prime, y_prime, r): 
                has_collision = True
                break
        if not has_collision:
            return y

def swarmplot_inner(X, C, y_offset = 0, r=0.05, ax=None):
    Y = np.zeros_like(X)
    if ax == None:
        fig, ax = plt.subplots()
    for i in range(len(X)):
        collisions = []
        for j in range(i-1,0,-1):
            if X[i] - X[j] > 2 * r:
                break
            else:
                collisions.append((X[j], Y[j]))

        candidate_ys = [0]
        for (x_prime, y_prime) in collisions:
            candidate_ys.append(y_prime + np.sqrt(np.abs((2 * r) ** 2 - (X[i] - x_prime) ** 2)))
            candidate_ys.append(y_prime - np.sqrt(np.abs((2 * r) ** 2 - (X[i] - x_prime) ** 2)))
        
        Y[i] = check_collisions(candidate_ys, collisions, X[i], r)

    landborn.scatterplot(None, X, y_offset + Y, color=C, ax=ax)
    
def swarmplot(df, categorical_data, numerical_data, r=0.5, ax=None, save_path=None):
    if ax == None:
        fig, ax = plt.subplots()
    categories = df[categorical_data].unique()
    counter = 0
    colors = ['red', 'green', 'blue']
    for category in categories:
        passed_data = list(df.loc[df[categorical_data] == category][numerical_data])
        swarmplot_inner(passed_data, colors[counter], y_offset=counter,r=r, ax=ax)
        counter += 1
    ax.set_ylabel(categorical_data)
    ax.set_xlabel(numerical_data)
    plt.gca().set_aspect('equal', adjustable='box')
    if save_path:
        plt.savefig(save_path)

if __name__ == '__main__':
    np.random.seed(120)
    data = pd.DataFrame({
    'Category': ['A']*80 + ['B']*80 + ['C']*80,
    'Value': np.concatenate([np.random.randint(0, 20, size=80), np.random.randint(20, 30, size=80), np.random.randint(30, 50, size=80)])
    })
    swarmplot(data, 'Category', 'Value', r=0.8, save_path='test_swarmplot_confirmed.png')