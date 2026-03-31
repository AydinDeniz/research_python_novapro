import networkx as nx
import matplotlib.pyplot as plt

class TaskManager:
    def __init__(self):
        self.dag = nx.DiGraph()

    def add_task(self, task_id, duration, dependencies=None):
        if dependencies is None:
            dependencies = []
        self.dag.add_node(task_id, duration=duration)
        for dependency in dependencies:
            self.dag.add_edge(dependency, task_id)

    def visualize_dag(self):
        pos = nx.spring_layout(self.dag)
        nx.draw(self.dag, pos, with_labels=True, node_size=7000, node_color="skyblue", font_size=20, font_weight="bold", arrowsize=20)
        labels = nx.get_node_attributes(self.dag, 'duration')
        nx.draw_networkx_labels(self.dag, pos, labels, font_color='red')
        plt.show()

    def get_execution_order(self):
        return list(nx.topological_sort(self.dag))

    def estimate_total_duration(self):
        execution_order = self.get_execution_order()
        total_duration = 0
        for task_id in execution_order:
            total_duration += self.dag.nodes[task_id]['duration']
        return total_duration

if __name__ == "__main__":
    manager = TaskManager()

    # Add tasks with dependencies and durations
    manager.add_task("A", 5)
    manager.add_task("B", 3, ["A"])
    manager.add_task("C", 4, ["A"])
    manager.add_task("D", 2, ["B", "C"])
    manager.add_task("E", 6, ["D"])

    # Visualize the DAG
    manager.visualize_dag()

    # Get execution order
    execution_order = manager.get_execution_order()
    print("Execution Order:", execution_order)

    # Estimate total duration
    total_duration = manager.estimate_total_duration()
    print("Total Duration:", total_duration)