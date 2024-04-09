<div class='data_display'>
    % if third_party.is_company():
        <% datas = (
        ("TVA intracommunautaire", third_party.tva_intracomm),
        ("Compte CG", third_party.compte_cg),
        ("Compte Tiers", third_party.compte_tiers),) %>
    %else:
        <% datas = (
        ("Compte CG", third_party.compte_cg),
        ("Compte Tiers", third_party.compte_tiers),) %>
    % endif
    <dl class="data_number">
        % for label, value in datas :
            <div>
                <dt>${label}</dt>
                <dd>
                    % if value:
                        ${value}
                    % else:
                        <em>Non renseigné</em>
                    % endif
                </dd>
            </div>
        % endfor
    </dl>
</div>