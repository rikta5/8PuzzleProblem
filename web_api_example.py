from flask import Flask, request, jsonify
from flask_cors import CORS
from src.domain import SlidingPuzzleProblem
from src.algorithms import (
    misplaced_tiles_heuristic,
    manhattan_distance_heuristic,
    linear_conflict_heuristic,
    AStarSearch,
    GreedyBestFirstSearch,
    HillClimbingSearch,
    SimulatedAnnealingSearch,
    IDAStarSearch,
    GeneticAlgorithmSearch,
)
from src.core import SearchAgent

app = Flask(__name__, static_folder='web_demo', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/solve', methods=['POST'])
def solve_puzzle():
    """
    Endpoint for the website to call.
    Expects JSON data: { 
        "size": 3, 
        "state": [...],
        "algorithm": "astar_manhattan" 
    }
    """
    data = request.json
    size = data.get('size', 3)
    initial_state = tuple(data.get('state'))
    algo_name = data.get('algorithm', 'astar_manhattan')
    
    problem = SlidingPuzzleProblem(size=size, initial_state=initial_state)
    
    h_manhattan = manhattan_distance_heuristic(problem.goal_state, problem.size)
    h_misplaced = misplaced_tiles_heuristic(problem.goal_state)
    h_linear = linear_conflict_heuristic(problem.goal_state, problem.size)
    
    if algo_name == "astar_manhattan":
        algo = AStarSearch(h_manhattan)
    elif algo_name == "astar_weighted":
        algo = AStarSearch(h_manhattan, weight=1.5)
    elif algo_name == "astar_linear":
        algo = AStarSearch(h_linear)
    elif algo_name == "astar_misplaced":
        algo = AStarSearch(h_misplaced)
    elif algo_name == "greedy_manhattan":
        algo = GreedyBestFirstSearch(h_manhattan)
    elif algo_name == "hill_climbing_manhattan":
        algo = HillClimbingSearch(h_manhattan, max_steps=2000)
    elif algo_name == "sa_manhattan":
        algo = SimulatedAnnealingSearch(h_manhattan)
    elif algo_name == "idastar_manhattan":
        algo = IDAStarSearch(h_manhattan)
    elif algo_name == "idastar_linear":
        algo = IDAStarSearch(h_linear)
    elif algo_name == "genetic_manhattan":
        algo = GeneticAlgorithmSearch(h_manhattan)
    else:
        return jsonify({"success": False, "error": "Unknown algorithm"})

    agent = SearchAgent(problem, algo)
    
    result = agent.solve()
    
    response = {
        "success": result.success,
        "actions": [node.action for node in result.solution_path if node.action],
        "nodes_expanded": result.nodes_expanded,
        "time_taken": result.runtime,
        "solution_cost": result.solution_cost if hasattr(result, 'solution_cost') else len(result.solution_path)
    }
    
    return jsonify(response)

if __name__ == '__main__':
    print("Starting AI Solver Server on port 5000...")
    app.run(debug=True, port=5000)
