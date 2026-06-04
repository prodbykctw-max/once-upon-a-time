extends CharacterBody2D
## PorcelainGuest.gd
## First enemy — a frozen wedding guest that wakes when player approaches.

@export var max_hp: int = 3
@export var move_speed: float = 50.0
@export var detect_range: float = 280.0
@export var attack_range: float = 60.0
@export var contact_damage: int = 1
@export var gravity: float = 900.0

enum State { SLEEP, WAKE, CHASE, ATTACK, HURT, DEAD }
var state: int = State.SLEEP
var hp: int
var facing: int = -1
var attack_cd: float = 0.0
var hurt_timer: float = 0.0

@onready var sprite: AnimatedSprite2D = get_node_or_null("Sprite")
var player: Node2D = null

func _ready() -> void:
	hp = max_hp
	add_to_group("enemy")
	await get_tree().process_frame
	player = get_tree().get_first_node_in_group("player")

func _physics_process(delta: float) -> void:
	if not is_on_floor():
		velocity.y += gravity * delta

	attack_cd = max(attack_cd - delta, 0.0)
	hurt_timer = max(hurt_timer - delta, 0.0)

	match state:
		State.SLEEP:   _process_sleep()
		State.WAKE:    _process_wake()
		State.CHASE:   _process_chase()
		State.ATTACK:  _process_attack(delta)
		State.HURT:    _process_hurt(delta)
		State.DEAD:    queue_free()

	if sprite:
		sprite.flip_h = facing > 0
	move_and_slide()

func _process_sleep() -> void:
	velocity.x = 0
	if player and global_position.distance_to(player.global_position) < detect_range:
		state = State.WAKE

func _process_wake() -> void:
	velocity.x = 0
	state = State.CHASE

func _process_chase() -> void:
	if not player:
		return
	var dist = global_position.distance_to(player.global_position)
	facing = sign(player.global_position.x - global_position.x)

	if dist < attack_range and attack_cd <= 0.0:
		state = State.ATTACK
		attack_cd = 1.6
		velocity.x = 0
	else:
		velocity.x = facing * move_speed

func _process_attack(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 200 * delta)
	await get_tree().create_timer(0.4).timeout
	if state == State.ATTACK:
		state = State.CHASE

func _process_hurt(delta: float) -> void:
	velocity.x = move_toward(velocity.x, 0, 600 * delta)
	if hurt_timer <= 0.0:
		state = State.CHASE if hp > 0 else State.DEAD

func take_damage(from_pos: Vector2, amount: int = 1) -> void:
	hp -= amount
	hurt_timer = 0.25
	state = State.HURT
	var dir = sign(global_position.x - from_pos.x)
	velocity.x = dir * 180
	velocity.y = -120
	if hp <= 0:
		state = State.DEAD
