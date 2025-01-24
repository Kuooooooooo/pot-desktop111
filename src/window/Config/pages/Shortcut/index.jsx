import { useConfig } from '../../../../hooks';
import { invoke } from '@tauri-apps/api/tauri';
import { Button, Card, CardBody } from '@nextui-org/react';
import { useTranslation } from 'react-i18next';
import { useEffect } from 'react';

export default function Shortcut() {
    const [translateShortcut, setTranslateShortcut] = useConfig('translate_shortcut', 'CommandOrControl+Alt+T');
    const { t } = useTranslation();

    useEffect(() => {
        // 在组件加载时注册快捷键
        invoke('register_translate_shortcut', { 
            shortcut: translateShortcut 
        }).catch(console.error);
    }, []);

    return (
        <Card>
            <CardBody>
                <div className="flex justify-between items-center">
                    <span>{t('config.shortcut.translate')}</span>
                    <div className="text-sm">
                        {translateShortcut}
                    </div>
                </div>
            </CardBody>
        </Card>
    );
} 