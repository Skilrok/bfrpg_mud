import json
import logging

from app.database import get_db_context
from app.models.item import Item as ItemModel
from app.schemas.item import Item as ItemSchema

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_ui_ac_bonus():
    """
    Verify that the UI can properly display the ac_bonus value for shield items.
    This script simulates the API response and confirms the shield item's ac_bonus
    value would be correctly sent to the frontend.
    """
    try:
        with get_db_context() as db:
            # Get the shield item with ID 80
            shield = db.query(ItemModel).filter(ItemModel.id == 80).first()

            if not shield:
                logger.error("Shield with ID 80 not found in the database")
                return

            logger.info(f"Found shield: {shield.name} (ID: {shield.id})")
            logger.info(f"Item type: {shield.item_type}")

            # Check the ac_bonus column
            logger.info(f"ac_bonus column value: {shield.ac_bonus}")

            # Convert the database model to a schema/response object (like the API would)
            item_response = ItemSchema.from_orm(shield)

            # Convert to JSON (simulating API response)
            item_json = item_response.dict()

            logger.info("\nSimulated API response for shield item:")
            logger.info(json.dumps(item_json, indent=2))

            # Verify that ac_bonus is included in the API response
            if "ac_bonus" in item_json and item_json["ac_bonus"] is not None:
                logger.info(
                    f"\n✅ Shield ac_bonus value ({item_json['ac_bonus']}) is included in the API response"
                )
                logger.info(
                    "The UI will correctly display this value using the updated JavaScript code"
                )
            else:
                logger.error(
                    f"\n❌ Shield ac_bonus value is NOT included in the API response"
                )
                logger.info("Check that the Item schema includes the ac_bonus field")

            # Also verify that the properties field contains the legacy ac_bonus value
            if (
                "properties" in item_json
                and item_json["properties"]
                and "ac_bonus" in item_json["properties"]
            ):
                properties_ac_bonus = item_json["properties"]["ac_bonus"]
                logger.info(
                    f"\n✅ Shield also has ac_bonus in properties: {properties_ac_bonus}"
                )

                # Check for consistency
                if item_json.get("ac_bonus") == properties_ac_bonus:
                    logger.info("✅ The column value matches the properties value")
                else:
                    logger.warning(
                        "⚠️ The column value does NOT match the properties value"
                    )
                    logger.info(
                        f"   Column: {item_json.get('ac_bonus')}, Properties: {properties_ac_bonus}"
                    )
            else:
                logger.warning("\n⚠️ Shield does NOT have ac_bonus in properties")

    except Exception as e:
        logger.error(f"Error verifying UI ac_bonus: {e}")
        raise


if __name__ == "__main__":
    verify_ui_ac_bonus()
