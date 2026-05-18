import React, { useState } from 'react';
import Select from '../components/common/Select';
import AppLayout from '../components/layout/AppLayout';
import PageHeader from '../components/layout/PageHeader';
import { authFieldClass, authLabelClass } from '../components/auth/AuthShell';
import { btnPrimary, pageCard } from '../components/layout/pageStyles';

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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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
    <AppLayout>
      <div className="max-w-2xl mx-auto">
        <PageHeader
          title="Возвраты"
          subtitle="Сообщите об ошибке или оформите возврат товара"
        />

        <div className={`${pageCard} p-8`}>
          {submitted ? (
            <div className="flex flex-col items-center justify-center py-12">
              <div className="bg-emerald-100 rounded-full p-4 mb-4">
                <i className="fa-solid fa-check text-emerald-700 text-2xl" />
              </div>
              <h2 className="text-xl font-semibold text-emerald-800 mb-2">Форма отправлена</h2>
              <p className="text-slate-600 text-center mb-6">
                Ваша заявка отправлена. Команда рассмотрит её и свяжется с вами при необходимости.
              </p>
              <button type="button" onClick={handleNewForm} className={btnPrimary}>
                <i className="fa-solid fa-plus mr-2" />
                Отправить ещё одну заявку
              </button>
            </div>
          ) : (
            <form className="space-y-6" onSubmit={handleSubmit}>
              <div>
                <label className={authLabelClass}>Штрих-код товара</label>
                <input
                  type="text"
                  name="barcode"
                  value={form.barcode}
                  onChange={handleChange}
                  className={authFieldClass}
                  placeholder="Сканируйте или введите штрих-код"
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
                <label className={authLabelClass}>Описание</label>
                <textarea
                  name="description"
                  value={form.description}
                  onChange={handleChange}
                  className={`${authFieldClass} min-h-[100px]`}
                  rows={4}
                  placeholder="Опишите проблему подробно"
                  required
                />
              </div>
              <div>
                <label className={authLabelClass}>Доказательство (фото, опционально)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="mt-1 block w-full text-sm text-slate-500"
                />
              </div>
              <div className="flex justify-end">
                <button type="submit" className={btnPrimary}>
                  <i className="fa-solid fa-paper-plane mr-2" />
                  Отправить
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </AppLayout>
  );
};

export default ErrorReturnFormPage;
