extends Node2D
## GownTrail.gd
## Secondary animation for Jandé's gown train.

@export var segment_count: int = 8
@export var segment_length: float = 6.0
@export var stiffness: float = 0.35
@export var damping: float = 0.85
@export var gravity_strength: float = 320.0
@export var velocity_influence: float = 0.45

var body_velocity: Vector2 = Vector2.ZERO
var velocity_delta: Vector2 = Vector2.ZERO
var body_facing: int = 1
var body_state: int = 0

var points: PackedVector2Array = []
var velocities: PackedVector2Array = []

@onready var line: Line2D = get_node_or_null("Line2D")

func _ready() -> void:
	points.resize(segment_count)
	velocities.resize(segment_count)
	for i in segment_count:
		points[i] = Vector2(-i * segment_length * body_facing, 0)
		velocities[i] = Vector2.ZERO

func _physics_process(delta: float) -> void:
	points[0] = Vector2.ZERO

	for i in range(1, segment_count):
		var trail_force = -body_velocity * velocity_influence * 0.01
		velocities[i].y += gravity_strength * delta
		velocities[i] += trail_force
		velocities[i] *= damping
		points[i] += velocities[i] * delta

		var to_prev = points[i] - points[i - 1]
		var dist = to_prev.length()
		if dist > segment_length:
			var correction = to_prev.normalized() * segment_length
			points[i] = points[i - 1] + correction * stiffness + to_prev * (1.0 - stiffness)

	if line:
		line.points = points
