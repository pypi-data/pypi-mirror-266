import os
import unittest
import shutil
import warnings
import json

from ceotr_config import ConfigAgent, DjangoConfigAgent, ConfigHandler
from ceotr_config.config_handler import load_yml_from_path
from ceotr_config.config_handler import dump_yml_to_path
from ceotr_config.config_handler import setting_file_path_validation
from ceotr_common_utilities.file_prepare import check_create_dir


class TestConfigYMLConfig(unittest.TestCase):
    def setUp(self):
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.setting_dir_name = "passwd"
        self.setting_file_name = "pw_info.yml"
        self.setting_path = os.path.join(*[self.output_path, self.setting_dir_name, self.setting_file_name])
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.config_obj = ConfigHandler(
            self.setting_path,  # testing setting path
            os.path.join(*[current_path, "resource", "default_setting.yml-tpl"]),  # test template path
            os.path.join(*[current_path, "resource", 'default_django_setting.yml-tpl']))
        self.tpl_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource")


    def test_load_default_yml_tpl(self):
        yml_dict = self.config_obj.load_default_yml_template()
        self.assertEqual(yml_dict["general_info"]["ENVIRONMENT"], "ENVIRONMENT")

    def test_yml_templates_with_no_overlap(self):
        # load real template and merge
        # Test template merge with no overlap template
        default_yml_dict = self.config_obj.load_default_yml_template()
        tpl_path = os.path.join(self.tpl_dir_path, 'default_setting.yml-tpl')
        user_yml_template = load_yml_from_path(tpl_path)
        merged_yml = self.config_obj.merge_yml(default_yml_dict, user_yml_template)
        expected_yml = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": "",
            },
            "general_info": {
                "ENVIRONMENT": "ENVIRONMENT",
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        self.assertEqual(expected_yml, merged_yml)

    def test_merge_yml_templates_with_overlap(self):
        # Test template merge with overlap template
        default_yml_dict = self.config_obj.load_default_yml_template()
        tpl_path2 = os.path.join(self.tpl_dir_path, 'user_setting1.yml')
        user_yml_template2 = load_yml_from_path(tpl_path2)
        merged_yml2 = self.config_obj.merge_yml(default_yml_dict, user_yml_template2)
        expected_yml2 = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": "",
            },
            "general_info": {
                "ENVIRONMENT": "ENVIRONMENT",
                "SECRET_KEY": "",
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        self.assertEqual(expected_yml2, merged_yml2)

    def test_yml_templates_with_overlap_with_value(self):
        default_yml_dict = self.config_obj.load_default_yml_template()
        tpl_path2 = os.path.join(self.tpl_dir_path, 'user_setting2.yml')
        user_yml_template2 = load_yml_from_path(tpl_path2)
        merged_yml2 = self.config_obj.merge_yml(default_yml_dict, user_yml_template2)
        expected_yml2 = {
            "bugs": {
                "USER": "the_user",
                "HOST": "the_host",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "the_data_dir",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "the_data_dir",
                "WEB_HOOK_TOKEN": "git",
            },
            "general_info": {
                "ENVIRONMENT": "ENVIRONMENT",
                "SECRET_KEY": "key_keys",
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        self.assertEqual(expected_yml2, merged_yml2)

    def test_compare_yaml_dict_simple_for_same(self):
        test_dict1 = {
            "valur": "a"
        }
        self.assertFalse(self.config_obj.is_yaml_dict_different(test_dict1, test_dict1))

    def test_compare_yaml_simple_for_different(self):
        test_dict1 = {
            "value": "a",
            "value2": "b"
        }
        test_dict2 = {
            "value": "a",
            "value3": "d"
        }
        self.assertTrue(self.config_obj.is_yaml_dict_different(test_dict1, test_dict2))

    def test_compare_yaml_dict_complex_for_same(self):
        test_dict1 = {
            "value": "a",
            "value2": {
                "value3": 1,
                "value4": [1, 2],
                "value": "a",
                "value5": {
                    "value1": 2
                }
            }
        }
        self.assertFalse(self.config_obj.is_yaml_dict_different(test_dict1, test_dict1))

    def test_compare_yaml_dict_complex_for_different(self):
        test_dict1 = {
            "value": "a",
            "value2": {
                "value3": 1,
                "value4": [1, 2],
                "value": "a",
                "value5": {
                    "value1": 2
                }
            }
        }
        test_dict2 = {
            "value": "a",
            "value2": {
                "value3": 1,
                "value4": [1, 2],
                "value": "c",
                "value6": {
                    "value1": 2
                }
            }
        }
        self.assertTrue(self.config_obj.is_yaml_dict_different(test_dict1, test_dict2))

    def test_build_or_load_no_setting_file(self):
        # If there is not configration file placed in correct place, it should raise error
        try:
            self.setting_path = self.output_path
            self.config_obj.build_or_load()
        except FileNotFoundError:
            pass
        else:
            self.fail()

    def test_build_or_load_with_existing_incomplete_setting_file(self):

        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "value": "a"
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        try:
            self.config_obj.build_or_load()
        except (ValueError, AttributeError):
            pass
        else:
            self.fail()

    def test_build_or_load_with_existing_correct_setting_file(self):
        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": ""
            },
            "general_info": {
                "ENVIRONMENT": 'ENVIRONMENT',
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        try:
            self.config_obj.build_or_load()
        except ValueError:
            self.fail()

    def test_build_or_load_with_existing_correct_setting_file2(self):
        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "general_info": {
                "ENVIRONMENT": 'ENVIRONMENT',
            },
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": ""
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        try:
            self.config_obj.build_or_load()
        except ValueError:
            self.fail()

    def test_merge_yml_file(self):
        # make sure merged toward yml file doesn't change it's orignial value
        user_setting2 = os.path.join(self.tpl_dir_path, 'user_setting2.yml')
        user_setting3 = os.path.join(self.tpl_dir_path, 'user_setting3.yml')
        u2 = load_yml_from_path(user_setting2)
        u3 = load_yml_from_path(user_setting3)
        u2["general_info"]["SOME_THING"] = "2"

        merged = self.config_obj.merge_yml(u3, u2)
        self.assertEqual(u2, merged)

    def test_build_or_load_with_existing_incomplete_setting_file2(self):
        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": ""
            }
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        try:
            self.config_obj.build_or_load()
        except ValueError:
            pass
        else:
            self.fail()

    def test_build_or_load_with_existing_more_setting_file(self):
        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": ""
            },
            "general_info": {
                "ENVIRONMENT": 'ENVIRONMENT',
                'Something': "extra",
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        try:
            self.config_obj.build_or_load()
        except ValueError:
            self.fail()

    def test_setting_file_path_validation(self):
        try:
            setting_file_path_validation(self.setting_path)
        except ValueError:
            self.fail()

        try:
            setting_file_path_validation(self.output_path)
        except ValueError:
            pass
        else:
            self.fail()

    def test_unchanged_field(self):
        self.config_obj.check_value_update=True
        passwd = check_create_dir(os.path.join(self.output_path, self.setting_dir_name))
        setting_path = os.path.join(passwd, self.setting_file_name)
        example_yaml_dict = {
            "bugs": {
                "USER": "",
                "HOST": "",
                "SLOCUM_DELAY_BINARY_DATA_DIR": "",
                "SLOCUM_LIVE_BINARY_DATA_DIR": "",
                "WEB_HOOK_TOKEN": "WEB_HOOK_TOKEN"
            },
            "general_info": {
                "ENVIRONMENT": 'ENVIRONMENT',
            },
            "django_settings": {
                "SECRET_KEY": "SECRET_KEY",
            }
        }
        dump_yml_to_path(setting_path, example_yaml_dict)
        self.config_obj.build_or_load()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            self.config_obj.build_or_load()
            assert len(w) == 1
            assert "SECRET_KEY" in str(w[-1].message)
            assert "ENVIRONMENT" in str(w[-1].message)

    def tearDown(self):
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        for the_file in os.listdir(self.output_path):
            file_path = os.path.join(self.output_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)




class ConfigHandleTestWithEnvVariable(unittest.TestCase):
    def setUp(self):
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.setting_dir_name = "passwd"
        self.setting_file_name = "pw_info.yml"
        self.setting_path = os.path.join(*[self.output_path, self.setting_dir_name, self.setting_file_name])
        current_path = os.path.dirname(os.path.abspath(__file__))
        self.config_obj = ConfigHandler(
            self.setting_path,
            os.path.join(*[current_path, "resource", "default_setting.yml-tpl"]),
            'default_django_setting.yml-tpl')
        self.tpl_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource")
        self.os_env_backup = dict(os.environ)

    def test_build_or_load_with_env_variable(self):
        os.environ["ENVIRONMENT"] = "docker"
        os.environ["BUGS_USER"] = "bugs_user"
        os.environ["BUGS_HOST"] = "bugs_host"

        setting_path = os.path.join(self.output_path, "config.yml")
        self.config_obj.setting_path = setting_path
        self.config_obj.check_value_update = False
        res = self.config_obj.build_or_load()
        expected = {'bugs': {'HOST': 'bugs_host', 'SLOCUM_DELAY_BINARY_DATA_DIR': '', 'SLOCUM_LIVE_BINARY_DATA_DIR': '',
                             'USER': 'bugs_user', 'WEB_HOOK_TOKEN': ''},
                    'django_settings': {'SECRET_KEY': 'SECRET_KEY'},
                    'general_info': {'ENVIRONMENT': 'ENVIRONMENT'}}
        self.assertEqual(expected, res)

    def test_load_environment_variable(self):
        ret_dict = {
            "database": {
                "name": "",
                "db": ""
            }
        }
        os.environ["DATABASE_NAME"] = "test_name"
        res = self.config_obj.load_environment_variable(ret_dict)
        expect_dict = {
            "database": {
                "name": "test_name",
                "db": ""
            }
        }
        self.assertEqual(res, expect_dict)

    def test_with_no_environment_config(self):
        self.config_obj.check_value_update = False
        # Get the absolute path of the current file
        current_file_path = os.path.abspath(__file__)
        # Get the directory of the current file
        current_dir = os.path.dirname(current_file_path)
        root_dir = os.path.dirname(current_dir)
        dch = ConfigAgent()
        dch.load(setting_path=os.path.join(root_dir, "resource/pw_info.yml"),
                 setting_template=os.path.join(current_dir, "resource/config_template.yml.stock"))
        except_database_value = {'NAME': '1', 'USER': '1', 'PASSWORD': '1'}
        self.assertEqual(except_database_value, dch.database)

    def tearDown(self):
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        for the_file in os.listdir(self.output_path):
            file_path = os.path.join(self.output_path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

        os.environ.clear()

        # Restore the environment variables from the backup
        for key, value in self.os_env_backup.items():
            os.environ[key] = value





class ConfigAgentFunctionTest(unittest.TestCase):
    def setUp(self):
        self.agent = DjangoConfigAgent()
        self.agent2 = ConfigAgent()
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        self.resource = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource")
        self.setting_path = os.path.join(self.resource, "passwd/pw_info.yml")
        self.tpl_path = os.path.join(self.resource, 'default_setting.yml-tpl')

    def test_load(self):
        self.agent.load(self.setting_path, self.tpl_path)
        self.assertTrue(hasattr(self.agent, 'general_info'))
        self.assertTrue(hasattr(self.agent, 'bugs'))

    def test_DEBBUG_value_for_prod(self):
        self.agent.load(self.setting_path, self.tpl_path)
        self.assertFalse(self.agent.debug)

    def test_DEBUG_value_before_load(self):
        self.assertTrue(self.agent.debug)


if __name__ == '__main__':
    unittest.main()
