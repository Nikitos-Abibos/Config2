import os
import sys
import git
import argparse
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description='Visualize dependency graph of git commits.')
    parser.add_argument('visualizer', help='Path to the graph visualizer (mermaid-cli).')
    parser.add_argument('repo', help='Path to the git repository.')
    parser.add_argument('-o', '--output', help='Output directory for the graph image.', default=os.getcwd())
    return parser.parse_args()

def get_commit_dependencies(repo_path):
    try:
        repo = git.Repo(repo_path)
        commit_graph = {}
        
        for commit in repo.iter_commits():
            commit_graph[commit.hexsha] = {
                'message': commit.message.strip(),
                'files': list(commit.stats.files.keys()),  
                'parents': [parent.hexsha for parent in commit.parents]
            }
        
        return commit_graph
    except git.exc.InvalidGitRepositoryError:
        print(f"Error: '{repo_path}' is not a valid Git repository.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def generate_mermaid_graph(commit_graph):
    mermaid_graph = "graph TD;\n"  
    files = set()
    
    for commit_sha, data in commit_graph.items():
        # Добавляем узел для коммита
        mermaid_graph += f"    {commit_sha}({data['message'].replace('(', '').replace(')', '')})\n"
        
        # Добавляем ребра от родителей к коммиту
        for parent in data['parents']:
            mermaid_graph += f"    {parent} --> {commit_sha}\n"
        
        # Добавляем ребра от коммита к файлам
        for file in data['files']:
            if file not in files:
                files.add(file)
                mermaid_graph += f"    {file}({file})\n"
            mermaid_graph += f"    {commit_sha} --> {file}\n"
    
    return mermaid_graph

def visualize_graph(mermaid_graph, visualizer_path, output_dir):
    try:
        with open(os.path.join(output_dir, 'graph.mmd'), 'w') as f:
            f.write(mermaid_graph)

        subprocess.run(f"{visualizer_path} -i {os.path.join(output_dir, 'graph.mmd')} -o {os.path.join(output_dir, 'graph.png')}", shell=True)
        print("Graph visualized and saved as graph.png")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def run_program(visualizer_path, repo_path, output_dir):
    commit_graph = get_commit_dependencies(repo_path)
    mermaid_graph = generate_mermaid_graph(commit_graph)
    visualize_graph(mermaid_graph, visualizer_path, output_dir)

def main():
    args = parse_arguments()
    run_program(args.visualizer, args.repo, args.output)

if __name__ == "__main__":
    main()

