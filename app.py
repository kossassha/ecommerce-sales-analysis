    )

    all_orders = len(order_level)

    cancel_rate = (
        cancelled_orders / all_orders * 100
        if all_orders > 0
        else 0
    )

    return_rate = (
        returned_orders / all_orders * 100
        if all_orders > 0
        else 0
    )

    q1, q2, q3, q4 = st.columns(4)

    with q1:
        metric_card(
            "Завершено",
            number(completed_orders),
        )

    with q2:
        metric_card(
            "Отменено",
            number(cancelled_orders),
        )

    with q3:
        metric_card(
            "Доля отмен",
            percent(cancel_rate),
        )

    with q4:
        metric_card(
            "Доля возвратов",
            percent(return_rate),
        )

    st.write("")

    status_table = pd.DataFrame(
        {
            "Статус": [
                "Завершено",
                "Отменено",
                "Возвращено",
            ],
            "Заказы": [
                completed_orders,
                cancelled_orders,
                returned_orders,
            ],
        }
    )

    status_table["Доля"] = (
        status_table["Заказы"]
        / status_table["Заказы"].sum()
        * 100
    )

    status_table["Доля"] = (
        status_table["Доля"]
        .map(lambda x: f"{x:.1f}%")
    )

    st.markdown(
        '<div class="section-title">Структура заказов</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        status_table,
        width="stretch",
        hide_index=True,
    )


# =========================================================
# ДАННЫЕ
# =========================================================

with tab_data:

    st.markdown(
        '<div class="section-title">Данные</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="small-muted">
            Строк: {number(len(filtered))}
            · Столбцов: {filtered.shape[1]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    csv = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Скачать CSV",
        data=csv,
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

    st.write("")

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
    )
