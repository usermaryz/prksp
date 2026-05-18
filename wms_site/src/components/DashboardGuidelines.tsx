import React from 'react';

export const DashboardGuidelines: React.FC = () => (
  <div className="dashboard-guidelines bg-white rounded-xl shadow p-6 max-w-md">
    <div className="dashboard-guidelines__title font-semibold text-lg mb-1">Инструкция</div>
    <div className="dashboard-guidelines__subtitle text-gray-500 text-sm mb-4">
      Как обрабатывать ошибки и возвраты
    </div>
    <ol className="dashboard-guidelines__steps space-y-3 mb-4">
      <li className="flex items-start gap-2">
        <i className="fa-solid fa-barcode text-slate-700 mt-1"></i>
        <div>
          <span className="font-semibold text-slate-800">Шаг 1: Сканируйте продукт</span>
          <div className="text-gray-600 text-sm">
            Используйте сканер штрих-кода для идентификации продукта. Можно ввести штрих-код
            вручную.
          </div>
        </div>
      </li>
      <li className="flex items-start gap-2">
        <i className="fa-regular fa-file-lines text-slate-700 mt-1"></i>
        <div>
          <span className="font-semibold text-slate-800">Шаг 2: Опишите проблему</span>
          <div className="text-gray-600 text-sm">
            Выберите тип ошибки и опишите детали. Будьте максимально конкретны.
          </div>
        </div>
      </li>
      <li className="flex items-start gap-2">
        <i className="fa-regular fa-image text-slate-700 mt-1"></i>
        <div>
          <span className="font-semibold text-slate-800">Шаг 3: Приложите доказательства</span>
          <div className="text-gray-600 text-sm">
            Загрузите фото повреждённого или неверного товара для подтверждения.
          </div>
        </div>
      </li>
      <li className="flex items-start gap-2">
        <i className="fa-solid fa-paper-plane text-slate-700 mt-1"></i>
        <div>
          <span className="font-semibold text-slate-800">Шаг 4: Отправьте заявку</span>
          <div className="text-gray-600 text-sm">
            Отправьте форму на проверку. Отдел контроля качества рассмотрит заявку и примет меры.
          </div>
        </div>
      </li>
    </ol>
    <div className="dashboard-guidelines__note bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded mb-4 flex items-start gap-2">
      <i className="fa-solid fa-triangle-exclamation text-yellow-500 mt-1"></i>
      <div className="text-sm text-yellow-800">
        <span className="font-semibold">Важно!</span>
        <br />
        Все возвраты должны быть обработаны в течение 24 часов с момента получения. Повреждённые
        товары необходимо сфотографировать до обработки.
      </div>
    </div>
    <a
      href="/files/return-policy.rtf"
      download="Политика возврата.rtf"
      className="dashboard-guidelines__download bg-slate-100 hover:bg-slate-100 text-slate-800 font-semibold px-4 py-2 rounded flex items-center gap-2"
    >
      <i className="fa-solid fa-download"></i>
      Скачать политику возврата
    </a>
  </div>
);
