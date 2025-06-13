import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file (str): 配置文件路径，默认为项目根目录下的config/sms_config.json
        """
        if config_file is None:
            # 获取项目根目录
            current_dir = Path(__file__).parent.parent.parent
            config_file = current_dir / "config" / "sms_config.json"
        
        self.config_file = Path(config_file)
        self._config = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not self.config_file.exists():
                # 如果配置文件不存在，创建默认配置
                self._create_default_config()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
                
            # 用环境变量覆盖配置文件中的值
            self._override_with_env_vars()
                
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        default_config = {
            "sms": {
                "api_url": "https://api.4321.sh/sms/template",
                "apikey": "",
                "secret": "",
                "sign_id": "",
                "template_id": "",
                "timeout": 30
            },
            "settings": {
                "retry_times": 3,
                "retry_delay": 1
            }
        }
        
        # 确保目录存在
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
    
    def _override_with_env_vars(self) -> None:
        """用环境变量覆盖配置"""
        if not self._config:
            return
        
        # 环境变量映射
        env_mappings = {
            'SMS_API_URL': 'sms.api_url',
            'SMS_APIKEY': 'sms.apikey',
            'SMS_SECRET': 'sms.secret',
            'SMS_SIGN_ID': 'sms.sign_id',
            'SMS_TEMPLATE_ID': 'sms.template_id',
            'SMS_TIMEOUT': 'sms.timeout',
            'SMS_RETRY_TIMES': 'settings.retry_times',
            'SMS_RETRY_DELAY': 'settings.retry_delay'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 处理数字类型
                if config_key in ['sms.timeout', 'settings.retry_times', 'settings.retry_delay']:
                    try:
                        env_value = int(env_value)
                    except ValueError:
                        continue
                
                # 设置配置值
                self._set_nested_value(self._config, config_key, env_value)
    
    def _set_nested_value(self, config: Dict, key: str, value: Any) -> None:
        """设置嵌套配置值"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get_sms_config(self) -> Dict[str, Any]:
        """
        获取短信配置
        
        Returns:
            Dict[str, Any]: 短信配置字典
        """
        if not self._config:
            raise ValueError("配置未加载")
        
        return self._config.get('sms', {})
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取指定配置项
        
        Args:
            key (str): 配置键，支持点号分隔的嵌套键，如 'sms.apikey'
            default (Any): 默认值
            
        Returns:
            Any: 配置值
        """
        if not self._config:
            raise ValueError("配置未加载")
        
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        self._load_config()
    
    def update_config(self, key: str, value: Any) -> None:
        """
        更新配置项并保存到文件
        
        Args:
            key (str): 配置键，支持点号分隔的嵌套键
            value (Any): 新值
        """
        if not self._config:
            raise ValueError("配置未加载")
        
        keys = key.split('.')
        config = self._config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
        
        # 保存到文件
        self._save_config()
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            # 确保目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
                
        except Exception as e:
            raise Exception(f"保存配置文件失败: {e}")
    
    def validate_sms_config(self) -> bool:
        """
        验证短信配置是否完整
        
        Returns:
            bool: 配置是否有效
        """
        sms_config = self.get_sms_config()
        required_fields = ['apikey', 'secret', 'sign_id', 'template_id']
        
        for field in required_fields:
            if not sms_config.get(field):
                print(f"警告: SMS配置中缺少必需字段 '{field}'")
                return False
        
        return True


# 全局配置管理器实例
config_manager = ConfigManager()


def get_sms_config() -> Dict[str, Any]:
    """
    获取短信配置的便捷函数
    
    Returns:
        Dict[str, Any]: 短信配置
    """
    return config_manager.get_sms_config()


def get_config(key: str, default: Any = None) -> Any:
    """
    获取配置的便捷函数
    
    Args:
        key (str): 配置键
        default (Any): 默认值
        
    Returns:
        Any: 配置值
    """
    return config_manager.get_config(key, default)


def validate_config() -> bool:
    """
    验证配置是否有效
    
    Returns:
        bool: 配置是否有效
    """
    return config_manager.validate_sms_config() 