from randomizer import Random

class CustomNameGenerator:
    def retrieve_metadata(self, custom_name_tag):
        # print(f"custom_name_tag:{custom_name_tag}")
        if '_generate_custom_name' in custom_name_tag:
            custom_name_tag = custom_name_tag['_generate_custom_name']
        prefix = custom_name_tag.get('prefix', '')
        suffix = custom_name_tag.get('suffix', '')
        # print(f"prefix:{prefix}, suffix:{suffix}")
        return prefix, suffix

    def generate_custom_name(self, custom_name_tag):
        if not custom_name_tag:
            return None

        prefix, suffix = self.retrieve_metadata(custom_name_tag)

        if suffix == "Military Alphabet":
            name_part = Random.military_alphabet_phrase(length=1)
        elif suffix == "Date Time":
            name_part = Random.fake_datetime()
        else:
            name_part = ""

        custom_name = f"{prefix}{name_part}"
        # print(f"custom_name:{custom_name}")
        return custom_name
