=============================================
ManipulateQuerySet Package Documentation
=============================================

Overview
========

The ``ManipulateQuerySet`` class, part of the ``django-ws-scoring`` package, enhances Django querysets by applying custom relevancy scores. It analyzes user history, such as search terms and locations, to dynamically adjust the relevance of queryset items. This functionality is designed to improve user experience in data-driven Django applications by providing personalized content ranking and search result customization.

Features
========

- **Preprocess User History**: Assigns relevancy weights to user history data based on the recency and frequency of search terms and locations.

- **Calculate Relevancy**: Dynamically adjusts the relevancy of queryset items based on calculated scores and defined field weights.

- **Customizable Field Weights**: Allows setting flexible weights for different model fields to fine-tune the relevancy scoring mechanism.

Dependencies
============

- Django
- Pandas
- Numpy
- django-pandas

To install these dependencies, run:

.. code-block:: sh

    pip install django pandas numpy django-pandas

Usage
=====

To utilize the ``ManipulateQuerySet`` class within your Django project, follow this example where user history data influences the ranking of job listings.

Defining User History Model
---------------------------

Assuming ``UserHistory`` is a model that captures user interactions:

.. code-block:: python

    from django.db import models
    import uuid

    class UserHistory(models.Model):
        keyword_search = models.TextField(null=True, blank=True)
        location_search = models.CharField(max_length=255, null=True, blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        session_id = models.UUIDField(default=uuid.uuid4, editable=False)

Applying ``ManipulateQuerySet``
-------------------------------

In your view or queryset logic:

.. code-block:: python

    import ws_scoring.module_ws_scoring as ws
    from myapp.models import UserHistory
    import uuid

    def get_annotated_queryset(request):
        user_history = UserHistory.objects.filter(
            session_id=uuid.UUID('12345678-1234-5678-1234-567812345678')
        )

        field_weight_dict = {
            'title': 10,
            'location': 7,
        }

        manipulator = ws.ManipulateQuerySet(
            queryset=JobListing.objects.prefetch_related('location'),
            user_history=user_history,
            field_weight_dict=field_weight_dict,
        )

        annotated_qs = manipulator.calculate_relevancy()

        return annotated_qs

This script retrieves ``UserHistory`` records for a specified ``session_id``, defines weights for the ``title`` and ``location`` fields of the ``JobListing`` model, and applies ``ManipulateQuerySet`` to calculate and adjust relevancy scores, producing an annotated queryset.

Customization
=============

Adjust the ``field_weight_dict`` to include any relevant fields for your application, modifying the weights to reflect their significance in relevancy scoring.

For comprehensive documentation on Django's model queries and queryset manipulation, refer to the `Django documentation <https://docs.djangoproject.com/en/stable/topics/db/queries/>`_.
