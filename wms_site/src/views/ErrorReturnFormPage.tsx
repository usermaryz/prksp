import React, { useState } from 'react';
import Navigation from '../components/Navigation';
import Select from '../components/common/Select';

const initialForm = {
  barcode: '',
  errorType: '',
  description: '',
  evidence: null as File | null,
};

const errorTypes = [
  { value: 'damaged', label: 'Повреждённый товар' },
  { value: 'wrong', label: 'Неверный товар' },
  { value: 'missing', label: 'Отсутствуют детали' },
  { value: 'other', label: 'Другое' },
];

const ErrorReturnFormPage: React.FC = () => {
  const [form, setForm] = useState(initialForm);
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  };

  const handleErrorTypeChange = (value: string) => {
    setForm(prev => ({ ...prev, errorType: value }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, evidence: e.target.files ? e.target.files[0] : null }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  const handleNewForm = () => {
    setForm(initialForm);
    setSubmitted(false);
  };

  return (
    <div className="error-return-form-page min-h-screen bg-gray-50">
      <Navigation active="Форма ошибки/возврата" />
      <div className="py-10">
        <header>
          <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">
              Форма ошибки/возврата
            </h1>
            <p className="mt-2 text-gray-500 text-sm">
              Сообщите об ошибке или оформите возврат товара. Пожалуйста, заполните форму ниже и
              приложите фото, если возможно.
            </p>
          </div>
        </header>
        <main>
          <div className="max-w-2xl mx-auto sm:px-6 lg:px-8">
            <div className="bg-white shadow rounded-lg p-8 mt-8">
              {submitted ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="bg-green-100 rounded-full p-4 mb-4">
                    <i className="fa-solid fa-check text-green-600 text-2xl"></i>
                  </div>
                  <h2 className="text-xl font-semibold text-green-700 mb-2">Форма отправлена</h2>
                  <p className="text-gray-600 text-center mb-6">
                    Ваша заявка на ошибку/возврат отправлена. Наша команда рассмотрит её и свяжется
                    с вами при необходимости.
                  </p>
                  <button
                    onClick={handleNewForm}
                    className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-semibold rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    <i className="fa-solid fa-plus mr-2"></i>
                    Отправить ещё одну заявку
                  </button>
                </div>
              ) : (
                <form className="space-y-6" onSubmit={handleSubmit}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Штрих-код товара
                    </label>
                    <input
                      type="text"
                      name="barcode"
                      value={form.barcode}
                      onChange={handleChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                      placeholder="Сканируйте или введите штрих-код товара"
                      required
                    />
                  </div>
                  <Select
                    value={form.errorType}
                    onChange={handleErrorTypeChange}
                    options={errorTypes}
                    label="Тип ошибки"
                    placeholder="Выберите тип ошибки"
                    required
                  />
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Описание</label>
                    <textarea
                      name="description"
                      value={form.description}
                      onChange={handleChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 text-sm"
                      rows={4}
                      placeholder="Опишите проблему подробно"
                      required
                    ></textarea>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Доказательство (фото, опционально)
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                      className="mt-1 block w-full text-sm text-gray-500"
                    />
                  </div>
                  <div className="flex justify-end">
                    <button
                      type="submit"
                      className="inline-flex items-center px-6 py-2 border border-transparent text-sm font-semibold rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                    >
                      <i className="fa-solid fa-paper-plane mr-2"></i>
                      Отправить
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ErrorReturnFormPage;
