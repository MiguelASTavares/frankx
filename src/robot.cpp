#include <frankx/robot.hpp>


namespace frankx {

Robot::Robot(std::string fci_ip): franka::Robot(fci_ip) {}

void Robot::setDefault() {
    setCollisionBehavior(
        {{20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0}},
        {{20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0}},
        {{20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0}},
        {{20.0, 20.0, 20.0, 10.0, 10.0, 10.0, 10.0}},
        {{20.0, 20.0, 20.0, 20.0, 20.0, 20.0}},
        {{20.0, 20.0, 20.0, 20.0, 20.0, 20.0}},
        {{20.0, 20.0, 20.0, 10.0, 10.0, 10.0}},
        {{20.0, 20.0, 20.0, 10.0, 10.0, 10.0}}
    );
    setJointImpedance({{3000, 3000, 3000, 2500, 2500, 2000, 2000}});
    setCartesianImpedance({{3000, 3000, 3000, 300, 300, 300}});
}

void Robot::setDynamicRel(double dynamic_rel) {
    velocity_rel = dynamic_rel;
    acceleration_rel = dynamic_rel;
    jerk_rel = dynamic_rel;
}

void Robot::move(const JointMotion& motion) {
    control(motion);
}

void Robot::move(const WaypointMotion& motion) {
    auto data = MotionData();
    move(motion, data);
}

void Robot::move(const WaypointMotion& motion, MotionData& data) {
    constexpr int degrees_of_freedoms {7};
    constexpr double control_rate {0.001};

    RMLPositionFlags flags;
    int result_value = 0;

    const auto rml = std::make_unique<ReflexxesAPI>(degrees_of_freedoms, control_rate);
    auto input_parameters = std::make_unique<RMLPositionInputParameters>(degrees_of_freedoms);
    auto output_parameters = std::make_unique<RMLPositionOutputParameters>(degrees_of_freedoms);

    setVector(input_parameters->SelectionVector, VectorCartRotElbow(true, true, true));
    setVector(input_parameters->MaxVelocityVector, VectorCartRotElbow(
        velocity_rel * max_translation_velocity,
        velocity_rel * max_rotation_velocity,
        velocity_rel * max_elbow_velocity
    ));
    setVector(input_parameters->MaxAccelerationVector, VectorCartRotElbow(
        acceleration_rel * max_translation_acceleration,
        acceleration_rel * max_rotation_acceleration,
        acceleration_rel * max_elbow_acceleration
    ));
    setVector(input_parameters->MaxJerkVector, VectorCartRotElbow(
        jerk_rel * max_translation_jerk,
        jerk_rel * max_rotation_jerk,
        jerk_rel * max_elbow_jerk
    ));

    WaypointMotion current_motion = motion;
    auto waypoint_iterator = current_motion.waypoints.begin();
    Vector7d old_vector = Vector7d::Zero();
    Eigen::Affine3d old_affine = Eigen::Affine3d::Identity();
    double old_elbow = 0.0;

    double time = 0.0;
    control([&](const franka::RobotState& robot_state, franka::Duration period) -> franka::CartesianPose {
        time += period.toSec();
        if (time == 0.0) {
            franka::CartesianPose initial_pose = franka::CartesianPose(robot_state.O_T_EE_c, robot_state.elbow_c);
            std::array<double, 7> initial_velocity = {robot_state.O_dP_EE_c[0], robot_state.O_dP_EE_c[1], robot_state.O_dP_EE_c[2], robot_state.O_dP_EE_c[3], robot_state.O_dP_EE_c[4], robot_state.O_dP_EE_c[5], robot_state.delbow_c[0]};

            Vector7d initial_vector = Affine(initial_pose).vector(initial_pose.elbow[0], old_vector);
            old_affine = Affine(initial_pose).data;
            old_vector = initial_vector;
            old_elbow = old_vector(6);

            setVector(input_parameters->CurrentPositionVector, initial_vector);
            setVector(input_parameters->CurrentVelocityVector, initial_velocity);
            setZero(input_parameters->CurrentAccelerationVector);

            Waypoint current_waypoint = *waypoint_iterator;
            Eigen::Affine3d target_affine = current_waypoint.getTargetAffine(old_affine).data;
            auto target_position_vector = current_waypoint.getTargetVector(old_affine, old_elbow, old_vector);
            setVector(input_parameters->TargetPositionVector, target_position_vector);
            setVector(input_parameters->TargetVelocityVector, current_waypoint.getTargetVelocity());

            if (current_waypoint.minimum_time.has_value()) {
                input_parameters->SetMinimumSynchronizationTime(current_waypoint.minimum_time.value());
            }

            old_affine = target_affine;
            old_vector = target_position_vector;
            old_elbow = old_vector(6);
        }

        for (auto& condition : data.conditions) {
            if (condition.has_fired) {
                continue;
            }

            if (condition.callback(robot_state, time)) {
                condition.has_fired = true;

                current_motion = *condition.action;
                waypoint_iterator = current_motion.waypoints.begin();
                Waypoint current_waypoint = *waypoint_iterator;

                franka::CartesianPose current_pose = franka::CartesianPose(robot_state.O_T_EE_c, robot_state.elbow_c);
                Vector7d current_vector = Affine(current_pose).vector(current_pose.elbow[0], old_vector);
                old_affine = Affine(current_pose).data;
                old_vector = current_vector;
                old_elbow = old_vector(6);

                auto target_position_vector = current_waypoint.getTargetVector(old_affine, old_elbow, old_vector);
                setVector(input_parameters->TargetPositionVector, target_position_vector);
                setVector(input_parameters->TargetVelocityVector, current_waypoint.getTargetVelocity());
            }
        }

        const int steps = std::max<int>(period.toMSec(), 1);
        for (int i = 0; i < steps; i++) {
            result_value = rml->RMLPosition(*input_parameters, output_parameters.get(), flags);

            if (result_value == ReflexxesAPI::RML_FINAL_STATE_REACHED) {
                waypoint_iterator += 1;

                if (waypoint_iterator == current_motion.waypoints.end()) {
                    return franka::MotionFinished(CartesianPose(input_parameters->CurrentPositionVector));
                }

                Waypoint current_waypoint = *waypoint_iterator;
                Eigen::Affine3d target_affine = current_waypoint.getTargetAffine(old_affine).data;
                auto target_position_vector = current_waypoint.getTargetVector(old_affine, old_elbow, old_vector);
                setVector(input_parameters->TargetPositionVector, target_position_vector);
                setVector(input_parameters->TargetVelocityVector, current_waypoint.getTargetVelocity());

                if (current_waypoint.minimum_time.has_value()) {
                    input_parameters->SetMinimumSynchronizationTime(current_waypoint.minimum_time.value());
                }

                old_affine = target_affine;
                old_vector = target_position_vector;
                old_elbow = old_vector(6);
            }

            *input_parameters->CurrentPositionVector = *output_parameters->NewPositionVector;
            *input_parameters->CurrentVelocityVector = *output_parameters->NewVelocityVector;
            *input_parameters->CurrentAccelerationVector = *output_parameters->NewAccelerationVector;
        }

        return CartesianPose(output_parameters->NewPositionVector);
    }, franka::ControllerMode::kCartesianImpedance);
}

} // namepace frankx