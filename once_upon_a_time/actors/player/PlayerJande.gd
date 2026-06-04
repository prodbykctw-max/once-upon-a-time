extends CharacterBody2D
## PlayerJande.gd
## Studio-quality 2.5D Metroidvania controller — Godot 4.6.2

@export_group("Run")
@export var max_run_speed: float       = 240.0
@export var run_accel: float           = 1800.0
@export var run_decel: float           = 2400.0
@export var air_accel: float           = 1100.0
@export var turn_boost: float          = 1.6

@export_group("Jump")
@export var jump_height: float         = 96.0
@export var jump_time_to_peak: float   = 0.36
@export var jump_time_to_fall: float   = 0.28
@export var max_fall_speed: float      = 900.0
@export var variable_jump_cut: float   = 0.45
@export var coyote_time: float         = 0.10
@export var jump_buffer_time: float    = 0.12

@export_group("Dash / Veil Step")
@export var dash_speed: float          = 520.0
@export var dash_duration: float       = 0.18
@export var dash_cooldown: float       = 0.45
@export var dash_iframes: float        = 0.14

var jump_velocity: float
var jump_gravity: float
var fall_gravity: float

enum State { IDLE, RUN, JUMP, FALL, DASH, ATTACK, HURT }
var state: int = State.IDLE

var has_dash: bool        = true
var has_double_jump: bool = false
var jumps_used: int       = 0
const MAX_AIR_JUMPS: int  = 1

var coyote_timer: float      = 0.0
var jump_buffer_timer: float = 0.0
var dash_timer: float        = 0.0
var dash_cd_timer: float     = 0.0
var iframe_timer: float      = 0.0

var facing: int = 1
var input_dir: float = 0.0

@onready var sprite: AnimatedSprite2D = $Sprite if has_node("Sprite") else null
@onready var gown_trail: Node2D = get_node_or_null("GownTrail")

func _ready() -> void:
	jump_velocity = -(2.0 * jump_height) / jump_time_to_peak
	jump_gravity  = (2.0 * jump_height) / (jump_time_to_peak * jump_time_to_peak)
	fall_gravity  = (2.0 * jump_height) / (jump_time_to_fall * jump_time_to_fall)
	add_to_group("player")

func _physics_process(delta: float) -> void:
	_read_input()
	_update_timers(delta)

	match state:
		State.DASH:   _process_dash(delta)
		State.ATTACK: _process_attack(delta)
		State.HURT:   _process_hurt(delta)
		_:            _process_normal(delta)

	move_and_slide()
	_update_animation()
	_update_gown_trail()

func _read_input() -> void:
	input_dir = Input.get_axis("move_left", "move_right")
	if input_dir != 0.0 and state != State.DASH:
		facing = sign(input_dir)

	if Input.is_action_just_pressed("jump"):
		jump_buffer_timer = jump_buffer_time

	if Input.is_action_just_pressed("dash") and has_dash and dash_cd_timer <= 0.0 and state != State.DASH:
		_enter_dash()

	if Input.is_action_just_pressed("attack") and state in [State.IDLE, State.RUN, State.JUMP, State.FALL]:
		_enter_attack()

func _update_timers(delta: float) -> void:
	coyote_timer       = max(coyote_timer - delta, 0.0)
	jump_buffer_timer  = max(jump_buffer_timer - delta, 0.0)
	dash_cd_timer      = max(dash_cd_timer - delta, 0.0)
	iframe_timer       = max(iframe_timer - delta, 0.0)

func _process_normal(delta: float) -> void:
	var on_ground := is_on_floor()

	if on_ground:
		coyote_timer = coyote_time
		jumps_used = 0

	var target := input_dir * max_run_speed
	var accel := run_accel if on_ground else air_accel
	if input_dir != 0.0 and sign(input_dir) != sign(velocity.x) and velocity.x != 0.0:
		accel *= turn_boost

	if input_dir != 0.0:
		velocity.x = move_toward(velocity.x, target, accel * delta)
	else:
		var decel := run_decel if on_ground else air_accel * 0.6
		velocity.x = move_toward(velocity.x, 0.0, decel * delta)

	var g := jump_gravity if velocity.y < 0.0 else fall_gravity
	velocity.y += g * delta
	velocity.y = min(velocity.y, max_fall_speed)

	if jump_buffer_timer > 0.0:
		if on_ground or coyote_timer > 0.0:
			_do_jump()
		elif has_double_jump and jumps_used < MAX_AIR_JUMPS:
			_do_jump()
			jumps_used += 1

	if Input.is_action_just_released("jump") and velocity.y < 0.0:
		velocity.y *= variable_jump_cut

	if not on_ground:
		state = State.JUMP if velocity.y < 0.0 else State.FALL
	else:
		state = State.RUN if abs(velocity.x) > 5.0 else State.IDLE

func _do_jump() -> void:
	velocity.y = jump_velocity
	jump_buffer_timer = 0.0
	coyote_timer = 0.0
	state = State.JUMP

func _enter_dash() -> void:
	state = State.DASH
	dash_timer = dash_duration
	dash_cd_timer = dash_cooldown
	iframe_timer = dash_iframes
	velocity.x = facing * dash_speed
	velocity.y = 0.0

func _process_dash(delta: float) -> void:
	dash_timer -= delta
	velocity.x = facing * dash_speed
	velocity.y = 0.0
	if dash_timer <= 0.0:
		velocity.x = facing * max_run_speed * 0.6
		state = State.FALL if not is_on_floor() else State.IDLE

var attack_timer: float = 0.0
const ATTACK_DURATION: float = 0.22

func _enter_attack() -> void:
	state = State.ATTACK
	attack_timer = ATTACK_DURATION

func _process_attack(delta: float) -> void:
	attack_timer -= delta
	if not is_on_floor():
		velocity.y += fall_gravity * delta
		velocity.y = min(velocity.y, max_fall_speed)
	velocity.x = move_toward(velocity.x, 0.0, run_decel * 0.5 * delta)
	if attack_timer <= 0.0:
		state = State.IDLE

const HURT_DURATION: float = 0.25
const HURT_KNOCKBACK: float = 220.0
var hurt_timer: float = 0.0

func take_damage(from_pos: Vector2, amount: int = 1) -> void:
	if iframe_timer > 0.0:
		return
	iframe_timer = 0.6
	hurt_timer = HURT_DURATION
	state = State.HURT
	var dir = sign(global_position.x - from_pos.x)
	velocity.x = dir * HURT_KNOCKBACK
	velocity.y = -180.0

func _process_hurt(delta: float) -> void:
	hurt_timer -= delta
	velocity.y += fall_gravity * delta
	velocity.x = move_toward(velocity.x, 0.0, run_decel * 0.4 * delta)
	if hurt_timer <= 0.0:
		state = State.IDLE

func _update_animation() -> void:
	if not sprite:
		return
	sprite.flip_h = facing < 0
	var anim := "idle"
	match state:
		State.IDLE:   anim = "idle"
		State.RUN:    anim = "run"
		State.JUMP:   anim = "jump"
		State.FALL:   anim = "fall"
		State.DASH:   anim = "dash"
		State.ATTACK: anim = "attack"
		State.HURT:   anim = "hurt"
	if sprite.sprite_frames and sprite.sprite_frames.has_animation(anim):
		if sprite.animation != anim:
			sprite.play(anim)

var _prev_velocity: Vector2 = Vector2.ZERO
func _update_gown_trail() -> void:
	if gown_trail == null:
		return
	gown_trail.set("body_velocity", velocity)
	gown_trail.set("body_facing",   facing)
	gown_trail.set("body_state",    state)
	gown_trail.set("velocity_delta", velocity - _prev_velocity)
	_prev_velocity = velocity
