# Prompt 98

import os
import subprocess
import networkx as nx
import matplotlib.pyplot as plt

def clone_repositories(repo_urls, local_path):
    for url in repo_urls:
        repo_name = url.split('/')[-1].replace('.git', '')
        repo_dir = os.path.join(local_path, repo_name)
        subprocess.run(['git', 'clone', url, repo_dir])

def extract_commits(repo_dir):
    commits = []
    result = subprocess.run(['git', 'log', '--pretty=format:%H'], cwd=repo_dir, stdout=subprocess.PIPE)
    for line in result.stdout.decode('utf-8').splitlines():
        commits.append(line.strip())
    return commits

def find_duplicate_fragments(repo_dirs):
    fragments = {}
    for repo_dir in repo_dirs:
        result = subprocess.run(['git', 'grep', '-n', '-o', '[a-zA-Z0-9_]+'], cwd=repo_dir, stdout=subprocess.PIPE)
        for line in result.stdout.decode('utf-8').splitlines():
            fragment = line.split(':')[-1].strip()
            if fragment in fragments:
                fragments[fragment].append(repo_dir)
            else:
                fragments[fragment] = [repo_dir]
    return {k: v for k, v in fragments.items() if len(v) > 1}

def create_dependency_graph(repo_dirs, duplicate_fragments):
    G = nx.Graph()
    for fragment, repos in duplicate_fragments.items():
        for repo in repos:
            if repo not in G:
                G.add_node(repo)
            for other_repo in repos:
                if other_repo!= repo and G.has_edge(repo, other_repo):
                    G[repo][other_repo]['weight'] += 1
                elif other_repo!= repo:
                    G.add_edge(repo, other_repo, weight=1)
    return G

def visualize_graph(G):
    pos = nx.spring_layout(G)
    edges, weights = zip(*nx.get_edge_attributes(G, 'weight').items())
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='skyblue', font_size=10, font_weight='bold', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=dict(zip(edges, weights)))
    plt.show()

def main():
    repo_urls = [
        'https://github.com/example/repo1.git',
        'https://github.com/example/repo2.git',
        'https://github.com/example/repo3.git'
    ]
    local_path = 'repos'

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    clone_repositories(repo_urls, local_path)
    repo_dirs = [os.path.join(local_path, url.split('/')[-1].replace('.git', '')) for url in repo_urls]

    duplicate_fragments = find_duplicate_fragments(repo_dirs)
    G = create_dependency_graph(repo_dirs, duplicate_fragments)
    visualize_graph(G)

if __name__ == "__main__":
    main()