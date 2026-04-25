from packages.models import Protocol, ProtocolStep


def generate_protocol() -> Protocol:
    return Protocol(
        protocol_id="P-001",
        name="Narrow Mn-doping boundary screen for LiFePO4",
        steps=[
            ProtocolStep(
                step_id="S1",
                name="Prepare candidate batches",
                resource_type="simulated_synthesis_station",
                duration_minutes=20,
                depends_on=[],
            ),
            ProtocolStep(
                step_id="S2",
                name="Run simulated synthesis",
                resource_type="simulated_synthesis_station",
                duration_minutes=30,
                depends_on=["S1"],
            ),
            ProtocolStep(
                step_id="S3",
                name="Validate structure",
                resource_type="structure_validator",
                duration_minutes=15,
                depends_on=["S2"],
            ),
            ProtocolStep(
                step_id="S4",
                name="Predict stability and conductivity proxy",
                resource_type="property_predictor",
                duration_minutes=15,
                depends_on=["S3"],
            ),
            ProtocolStep(
                step_id="S5",
                name="Validate result schema",
                resource_type="data_validation_engine",
                duration_minutes=5,
                depends_on=["S4"],
            ),
        ],
    )

